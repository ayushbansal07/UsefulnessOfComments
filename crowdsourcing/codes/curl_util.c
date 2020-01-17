/***************************************************************************
 *
 * Copyright (C) 1998 - 2019, Daniel Stenberg, <daniel@haxx.se>, et al.
 *
 * This software is licensed as described in the file COPYING, which
 * you should have received as part of this distribution. The terms
 * are also available at https://curl.haxx.se/docs/copyright.html.

 ***************************************************************************/
#include "server_setup.h"

#ifdef HAVE_SIGNAL_H
#include <signal.h>
#endif
#ifdef HAVE_NETINET_IN_H
#include <netinet/in.h>
#endif
#ifdef _XOPEN_SOURCE_EXTENDED
#include <arpa/inet.h>
#endif
#ifdef HAVE_NETDB_H
#include <netdb.h>
#endif
#ifdef HAVE_POLL_H
#include <poll.h>
#elif defined(HAVE_SYS_POLL_H)
#include <sys/poll.h>
#endif
#ifdef __MINGW32__
#include <w32api.h>
#endif

#define ENABLE_CURLX_PRINTF
/* make the curlx header define all printf() functions to use the curlx_*
   versions instead */
#include "curlx.h" /* from the private lib dir */
#include "getpart.h"
#include "util.h"
#include "timeval.h"

#ifdef USE_WINSOCK
#undef  EINTR
#define EINTR    4 /* errno.h value */
#undef  EINVAL
#define EINVAL  22 /* errno.h value */
#endif

/* MinGW with w32api version < 3.6 declared in6addr_any as extern,
   but lacked the definition */
#if defined(ENABLE_IPV6) && defined(__MINGW32__)
#if (__W32API_MAJOR_VERSION < 3) || \
    ((__W32API_MAJOR_VERSION == 3) && (__W32API_MINOR_VERSION < 6))
const struct in6_addr in6addr_any = {{ IN6ADDR_ANY_INIT }};
#endif /* w32api < 3.6 */
#endif /* ENABLE_IPV6 && __MINGW32__*/

static struct timeval tvnow(void);

/* This function returns a pointer to STATIC memory. It converts the given
 * binary lump to a hex formatted string usable for output in logs or
 * whatever.
 */
char *data_to_hex(char *data, size_t len)
{
  static char buf[256*3];
  size_t i;
  char *optr = buf;
  char *iptr = data;

  if(len > 255)
    len = 255;

  for(i = 0; i < len; i++) {
    if((data[i] >= 0x20) && (data[i] < 0x7f))
      *optr++ = *iptr++;
    else {
      msnprintf(optr, 4, "%%%02x", *iptr++);
      optr += 3;
    }
  }
  *optr = 0; /* in case no sprintf was used */

  return buf;
}

void logmsg(const char *msg, ...)
{
  va_list ap;
  char buffer[2048 + 1];
  FILE *logfp;
  struct timeval tv;
  time_t sec;
  struct tm *now;
  char timebuf[20];
  static time_t epoch_offset;
  static int    known_offset;

  if(!serverlogfile) {
    fprintf(stderr, "Error: serverlogfile not set\n");
    return;
  }

  tv = tvnow();
  if(!known_offset) {
    epoch_offset = time(NULL) - tv.tv_sec;
    known_offset = 1;
  }
  sec = epoch_offset + tv.tv_sec;
  now = localtime(&sec); /* not thread safe but we don't care */

  msnprintf(timebuf, sizeof(timebuf), "%02d:%02d:%02d.%06ld",
            (int)now->tm_hour, (int)now->tm_min, (int)now->tm_sec,
            (long)tv.tv_usec);

  va_start(ap, msg);
  mvsnprintf(buffer, sizeof(buffer), msg, ap);
  va_end(ap);

  logfp = fopen(serverlogfile, "ab");
  if(logfp) {
    fprintf(logfp, "%s %s\n", timebuf, buffer);
    fclose(logfp);
  }
  else {
    int error = errno;
    fprintf(stderr, "fopen() failed with error: %d %s\n",
            error, strerror(error));
    fprintf(stderr, "Error opening file: %s\n", serverlogfile);
    fprintf(stderr, "Msg not logged: %s %s\n", timebuf, buffer);
  }
}

#ifdef WIN32
/* uses global character buffer generated from message_generate function of sockfilt file*/
void win32_perror(const char *msg)
{
  char buf[512];
  DWORD err = SOCKERRNO;

  if(!FormatMessageA((FORMAT_MESSAGE_FROM_SYSTEM |
                      FORMAT_MESSAGE_IGNORE_INSERTS), NULL, err,
                     LANG_NEUTRAL, buf, sizeof(buf), NULL))
    msnprintf(buf, sizeof(buf), "Unknown error %lu (%#lx)", err, err);
  if(msg)
    fprintf(stderr, "%s: ", msg);
  fprintf(stderr, "%s\n", buf);
}
#endif  /* WIN32 */

#ifdef USE_WINSOCK
void win32_init(void)
{
  WORD wVersionRequested;
  WSADATA wsaData;
  int err;
  wVersionRequested = MAKEWORD(USE_WINSOCK, USE_WINSOCK);

  err = WSAStartup(wVersionRequested, &wsaData);

  if(err != 0) {
    perror("Winsock init failed");
    logmsg("Error initialising winsock -- aborting");
    exit(1);
  }

  if(LOBYTE(wsaData.wVersion) != USE_WINSOCK ||
     HIBYTE(wsaData.wVersion) != USE_WINSOCK) {
    WSACleanup();
    perror("Winsock init failed");
    logmsg("No suitable winsock.dll found -- aborting");
    exit(1);
  }
}

void win32_cleanup(void)
{
  WSACleanup();
}
#endif  /* USE_WINSOCK */

/* set by the main code to point to where the test dir is */
const char *path = ".";

char *test2file(long testno)
{
  static char filename[256];
  msnprintf(filename, sizeof(filename), TEST_DATA_PATH, path, testno);
  return filename;
}

/*
 * Portable function used for waiting a specific amount of ms.
 * Waiting indefinitely with this function is not allowed, a
 * zero or negative timeout value will return immediately.
 *
 * Return values:
 *   -1 = system call error, or invalid timeout value
 *    0 = specified timeout has elapsed
 */
int wait_ms(int timeout_ms)
{
#if !defined(MSDOS) && !defined(USE_WINSOCK)
#ifndef HAVE_POLL_FINE
  struct timeval pending_tv;
#endif
  struct timeval initial_tv;
  int pending_ms;
#endif
  int r = 0;

  if(!timeout_ms)
    return 0;
  if(timeout_ms < 0) {
    errno = EINVAL;
    return -1;
  }
#if defined(MSDOS)
  delay(timeout_ms);
#elif defined(USE_WINSOCK)
  Sleep(timeout_ms);
#else
  pending_ms = timeout_ms;
  initial_tv = tvnow();
  do {
    int error;
#if defined(HAVE_POLL_FINE)
    r = poll(NULL, 0, pending_ms);
#else
    pending_tv.tv_sec = pending_ms / 1000;
    pending_tv.tv_usec = (pending_ms % 1000) * 1000;
    r = select(0, NULL, NULL, NULL, &pending_tv);
#endif /* HAVE_POLL_FINE */
    if(r != -1)
      break;
    error = errno;
    if(error && (error != EINTR))
      break;
    pending_ms = timeout_ms - (int)timediff(tvnow(), initial_tv);
    if(pending_ms <= 0)
      break;
  } while(r == -1);
#endif /* USE_WINSOCK */
  if(r)
    r = -1;
  return r;
}

