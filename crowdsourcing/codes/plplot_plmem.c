
//  plmem.c
//
//  Copyright (C) 1992, 1993, 1994, 1995

//--------------------------------------------------------------------------
//

//! @file
//!  These functions provide allocation and deallocation of two-dimensional
//!  arrays.
//!

#include "plplotP.h"

//--------------------------------------------------------------------------
--------------------------------------------------------------------------

void
plStatic2dGrid( PLFLT_NC_MATRIX zIliffe, PLFLT_VECTOR zStatic, PLINT nx, PLINT ny )
{
    PLINT i;

    for ( i = 0; i < nx; i++ )
    {
        zIliffe[i] = (PLFLT_NC_SCALAR) ( zStatic + i * ny );
    }
}

//--------------------------------------------------------------------------
//
//! Allocate a block of memory for use as a matrix of type
//! PLFLT_MATRIX (organized as an Iliffe column vector of pointers to
//! row vectors).  As a result the matrix can be accessed using C/C++
//! syntax like *f[i][j]. The memory associated with this matrix must
//! be freed by calling plFree2dGrid once it is no longer required.
//! Example usage:
//!
//!   PLFLT **z;
//!
//!   plAlloc2dGrid(&z, XPTS, YPTS);
//!
//! @param f Location of the storage (address of a **).
//! @param nx Size of the grid in x.
//! @param ny Size of the grid in y.
//!
//--------------------------------------------------------------------------

void
plAlloc2dGrid( PLFLT ***f, PLINT nx, PLINT ny )
{
    PLINT i;

    if ( ( *f = (PLFLT **) calloc( (size_t) nx, sizeof ( PLFLT * ) ) ) == NULL )
        plexit( "Memory allocation error in \"plAlloc2dGrid\"" );

    for ( i = 0; i < nx; i++ )
    {
        if ( ( ( *f )[i] = (PLFLT *) calloc( (size_t) ny, sizeof ( PLFLT ) ) ) == NULL )
            plexit( "Memory allocation error in \"plAlloc2dGrid\"" );
    }
}

//  used extensively in resetting standard x-y plots, semi-log plots 


void
plFree2dGrid( PLFLT **f, PLINT nx, PLINT PL_UNUSED( ny ) )
{
    PLINT i;

    for ( i = 0; i < nx; i++ )
        free( (void *) f[i] );

    free( (void *) f );
}


