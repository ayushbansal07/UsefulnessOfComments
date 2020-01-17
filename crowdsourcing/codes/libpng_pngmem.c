/* pngmem.c - stub functions for memory allocation of libpng -- raster-graphics file-format
 */


/* Copyright (c)
 *
 * This code is released under the libpng license.
 * For conditions of distribution and use, see the disclaimer
 * and license in png.h
 */ 


 /* This file provides a location for all memory allocation.  Users who
 * need special memory handling are expected to supply replacement
 * functions for png_malloc() and png_free(), and to use
 * png_create_read_struct_2() and png_create_write_struct_2() to
 * identify the replacement functions.
 */

#include "pngpriv.h"
#include "pngstruct.h"
#if defined(PNG_READ_SUPPORTED) || defined(PNG_WRITE_SUPPORTED)
/* Free a png_struct */

/* png_destroy_png_struct calls png_free 
which  might call png_error and may certainly call
       * png_get_mem_ptr, so fake a temporary png_struct to support this.
       */
void  png_destroy_png_struct(png_structrp png_ptr)
{
   if (png_ptr != NULL)
   {
      
      png_struct dummy_struct = *png_ptr;
      memset(png_ptr, 0, (sizeof *png_ptr));
      png_free(&dummy_struct, png_ptr);

#     ifdef PNG_SETJMP_SUPPORTED
         /* We may have a jmp_buf left to deallocate. */
         png_free_jmpbuf(&dummy_struct);
#     endif
   }
}

/* Allocate memory.  For reasonable files, size should never exceed
 * 64K.  However, zlib may allocate more than 64K if you don't tell
 * it not to.  See zconf.h and png.h for more information.  zlib does
 * need to allocate exactly 64K, so whatever you call here must
 * have the ability to do that.
 */

/* uses png_calloc defined in pngriv.h*/
PNG_FUNCTION(png_voidp,PNGAPI
png_calloc,(png_const_structrp png_ptr, png_alloc_size_t size),PNG_ALLOCATED)
{
   png_voidp ret;

   ret = png_malloc(png_ptr, size);

   if (ret != NULL)
      memset(ret, 0, size);

   return ret;
}


#ifndef PNG_USER_MEM_SUPPORTED
   PNG_UNUSED(png_ptr)
#endif



#if defined(PNG_TEXT_SUPPORTED) || defined(PNG_sPLT_SUPPORTED) ||\
   defined(PNG_STORE_UNKNOWN_CHUNKS_SUPPORTED)
/* Introduced in libpng 1.6.0, commit 0e13545. This is really here only to work round a spurious warning in GCC 4.6 and 4.7
 * that arises because of the checks in png_realloc_array that are repeated in
 * png_malloc_array, issue #289.
 */
static png_voidp
png_malloc_array_checked(png_const_structrp png_ptr, int nelements,
    size_t element_size)
{
   png_alloc_size_t req = (png_alloc_size_t)nelements; /* known to be > 0 */

   if (req <= PNG_SIZE_MAX/element_size)
      return png_malloc_base(png_ptr, req * element_size);

  
   return NULL;
}



   /* Check for overflow on the elements count (so the caller does not have to
    * check.) png_malloc_array has been worked with the size calculations to avoid
          * overflow.
    */
PNG_FUNCTION(png_voidp,
png_realloc_array,(png_const_structrp png_ptr, png_const_voidp old_array,
    int old_elements, int add_elements, size_t element_size),PNG_ALLOCATED)
{
   /* These are internal errors: */
   if (add_elements <= 0 || element_size == 0 || old_elements < 0 ||
      (old_array == NULL && old_elements > 0))
      png_error(png_ptr, "internal error: array realloc");

   if (add_elements <= INT_MAX - old_elements)
   {
      png_voidp new_array = png_malloc_array_checked(png_ptr,
          old_elements+add_elements, element_size);

      if (new_array != NULL)
      {
         
         if (old_elements > 0)
            memcpy(new_array, old_array, element_size*(unsigned)old_elements);

         memset((char*)new_array + element_size*(unsigned)old_elements, 0,
             element_size*(unsigned)add_elements);

         return new_array;
      }
   }

   return NULL; /* error */
}
#endif /* TEXT || sPLT || STORE_UNKNOWN_CHUNKS */





/* Free a pointer allocated by png_malloc().  If ptr is NULL, return
 * without taking any action.
 */
void PNGAPI
png_free(png_const_structrp png_ptr, png_voidp ptr)
{
   if (png_ptr == NULL || ptr == NULL)
      return;

#ifdef PNG_USER_MEM_SUPPORTED
   if (png_ptr->free_fn != NULL)
      png_ptr->free_fn(png_constcast(png_structrp,png_ptr), ptr);

   else
      png_free_default(png_ptr, ptr);
}




#endif /* USER_MEM */
#endif /* READ || WRITE */