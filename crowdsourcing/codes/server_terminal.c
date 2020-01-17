/* terminal.c -- controlling the terminal with termcap. */

/* Copyright (C) 1996-2006 Free Software Foundation */

/* part of Readline library provides a set of functions for use by applications
that allow users to edit command lines as they are typed in.
These functions are basic functions are based on conditional processing of regular expressions. 
Uses functions and data types defined in readine and keyboard header files. 
Produces types which are used in  MariaDBbackup source files */


/* To build the library, try typing `./configure', then `make'..
If `configure' is given the `--enable-shared' option, it will attempt
to build the shared libraries by default on supported platforms.  Requires Linux distribution with gcc*/

#define READLINE_LIBRARY

#if defined (HAVE_CONFIG_H)
#  include "config_readline.h"
#endif

#include <sys/types.h>
#include "posixstat.h"
#include <fcntl.h>
#if defined (HAVE_SYS_FILE_H)
#  include <sys/file.h>
#endif /* HAVE_SYS_FILE_H */

#if defined (HAVE_UNISTD_H)
#  include <unistd.h>
#endif /* HAVE_UNISTD_H */

#if defined (HAVE_STDLIB_H)
#  include <stdlib.h>
#else
#  include "ansi_stdlib.h"
#endif /* HAVE_STDLIB_H */

#if defined (HAVE_LOCALE_H)
#  include <locale.h>
#endif

#include <stdio.h>

/* System-specific feature definitions and include files. */
#include "rldefs.h"

#if defined (GWINSZ_IN_SYS_IOCTL) && !defined (TIOCGWINSZ)
#  include <sys/ioctl.h>
#endif /* GWINSZ_IN_SYS_IOCTL && !TIOCGWINSZ */

/* tty driver-related definitions / types like 
_rl_tty_chars (used in this file) */
#include "rltty.h" 
#include "tcap.h"

/* Some standard library routines. */
#include "readline.h"
#include "history.h"

#include "rlprivate.h"
#include "rlshell.h"
#include "xmalloc.h"

#if defined (__MINGW32__)
#  include <windows.h>
#  include <wincon.h>

static void _win_get_screensize PARAMS((int *, int *));
#endif

#if defined (__EMX__)
static void _emx_get_screensize PARAMS((int *, int *));
#endif

#define CUSTOM_REDISPLAY_FUNC() (rl_redisplay_function != rl_redisplay)
#define CUSTOM_INPUT_FUNC() (rl_getc_function != rl_getc)

/*  If the calling application sets this to a non-zero value, readline will
    use the $LINES and $COLUMNS environment variables to set its idea of the
    window size before interrogating the kernel. */
int rl_prefer_env_winsize = 0;

/* **************************************************************** */
/*								    */
/*			Terminal and Termcap			    */
/*								    */
/* **************************************************************** */

/* Delete key */
static const char *_rl_term_kD;

/* Insert key */
static const char *_rl_term_kI;

/* Cursor control */
static const char *_rl_term_vs;	/* very visible */
static const char *_rl_term_ve;	/* normal */
static char *term_buffer = (char *)NULL;
static char *term_string_buffer = (char *)NULL;

static int tcap_initialized; // should have a value greater than 1, is taken from user

#if !defined (__linux__)
#  if defined (__EMX__) || defined (NEED_EXTERN_PC)
extern 
#  endif /* __EMX__ || NEED_EXTERN_PC */
char PC, *BC, *UP;
#endif /* __linux__ */

/* Non-zero if we determine that the terminal can do character insertion. */
int _rl_terminal_can_insert = 0;

/* used in character insertion in cursor functions below */
const char *_rl_term_im;
const char *_rl_term_ei;
const char *_rl_term_ic;


/* How to delete characters. */
const char *_rl_term_dc;
const char *_rl_term_DC;

const char *_rl_term_forward_char;

/* How to go up a line. */
const char *_rl_term_up;
char _rl_term_up_default[2] = { 0, 0 };


static const char *_rl_visible_bell;


int _rl_term_autowrap = -1;


static int term_has_meta;

static void bind_termcap_arrow_keys PARAMS((Keymap));

int _rl_screenwidth, _rl_screenheight, _rl_screenchars;


int _rl_enable_keypad;

/* Non-zero means the user wants to enable a meta key. */
int _rl_enable_meta = 1;

/* **************************************************************** */
/*								    */
/*	 		Controlling the Cursor			    */
/*								    */
/* **************************************************************** */

/* Set the cursor appropriately depending on IM, which is one of the
   insert modes (insert or overwrite).  Insert mode gets the normal
   cursor.  Overwrite mode gets a very visible cursor.  Only does
   anything if we have both capabilities. */
void
_rl_set_cursor (im, force)
     int im, force;
{
  if (_rl_term_ve && _rl_term_vs)
    {
      if (force || im != rl_insert_mode) // rl_insert_mode defined in config_readline.h
	{
	  if (im == RL_IM_OVERWRITE)
	    tputs (_rl_term_vs, 1, _rl_output_character_function);
	  else
	    tputs (_rl_term_ve, 1, _rl_output_character_function);
	}
    }
}