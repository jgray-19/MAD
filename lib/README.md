
# Native Apple Silicon dependencies

The `bin` submodule contains architecture-specific static archives. Rebuild
them as `arm64`; Intel (`x86_64`) archives cannot be linked into MAD.

## Toolchain and sources

```sh
brew install gcc cmake
export CC=gcc-15 CXX=g++-15 FC=gfortran-15
export MACOSX_DEPLOYMENT_TARGET=14
export MAD_ROOT=/path/to/MAD
export MAD_BIN="$MAD_ROOT/bin/macosx"
export MAD_DEPS=/private/tmp/mad-deps
git -C "$MAD_ROOT" submodule update --init bin
mkdir -p "$MAD_DEPS" && cd "$MAD_DEPS"
git clone --depth 1 --branch mad-patch https://github.com/MethodicalAcceleratorDesign/LuaJIT.git luajit
git clone --depth 1 https://github.com/MethodicalAcceleratorDesign/luafilesystem.git lfs
git clone --depth 1 --branch v3.12.1 https://github.com/Reference-LAPACK/lapack.git lapack
git clone --depth 1 --branch v2.7.1 https://github.com/stevengj/nlopt.git nlopt
curl -fLO https://www.fftw.org/fftw-3.3.10.tar.gz
curl -fLO https://www-user.tu-chemnitz.de/~potts/nfft/download/nfft-3.5.3.tar.gz
curl -fLO http://www.inf.puc-rio.br/~roberto/lpeg/lpeg-1.1.0.tar.gz
tar xzf fftw-3.3.10.tar.gz; tar xzf nfft-3.5.3.tar.gz; tar xzf lpeg-1.1.0.tar.gz
```

Replace the `-15` suffix with the Homebrew GCC version installed locally.

## Build archives

```sh
# LuaJIT
cd "$MAD_DEPS/luajit" && make clean && make -j"$(sysctl -n hw.ncpu)" amalg PREFIX="$PWD" CC="$CC" && make install PREFIX="$PWD"
cp src/libluajit.a "$MAD_BIN"

# FFTW
cd "$MAD_DEPS/fftw-3.3.10" && CC="$CC" CFLAGS='-O3 -fPIC' ./configure --disable-shared --enable-static && make -j"$(sysctl -n hw.ncpu)"
cp .libs/libfftw3.a "$MAD_BIN"

# LuaFileSystem
cd "$MAD_DEPS/lfs" && make clean && make lfs.a CC="$CC" AR=ar CFLAGS="-O3 -fPIC -I$MAD_DEPS/luajit/src"
cp liblfs.a "$MAD_BIN"

# LPeg: MAD embeds a static archive, so build the object set rather than the upstream shared-module target.
cd "$MAD_DEPS/lpeg-1.1.0" && make clean && make lpvm.o lpcap.o lptree.o lpcode.o lpprint.o lpcset.o CC="$CC" LUADIR="$MAD_DEPS/luajit/src" COPT='-O3 -DNDEBUG'
ar -rcs liblpeg.a lpvm.o lpcap.o lptree.o lpcode.o lpprint.o lpcset.o && cp liblpeg.a "$MAD_BIN"

# NLopt 2.7.1 needs this compatibility setting with current CMake.
cd "$MAD_DEPS/nlopt" && cmake -S . -B build-arm64 -DBUILD_SHARED_LIBS=OFF -DNLOPT_CXX=OFF -DNLOPT_FORTRAN=OFF -DCMAKE_C_COMPILER="$CC" -DCMAKE_OSX_ARCHITECTURES=arm64 -DCMAKE_POLICY_VERSION_MINIMUM=3.5
CMAKE_POLICY_VERSION_MINIMUM=3.5 cmake --build build-arm64 -j"$(sysctl -n hw.ncpu)" && cp build-arm64/libnlopt.a "$MAD_BIN"

# LAPACK and reference BLAS
cd "$MAD_DEPS/lapack" && cmake -S . -B build-arm64 -DBUILD_SHARED_LIBS=OFF -DBUILD_TESTING=OFF -DCMAKE_C_COMPILER="$CC" -DCMAKE_Fortran_COMPILER="$FC" -DCMAKE_OSX_ARCHITECTURES=arm64
cmake --build build-arm64 -j"$(sysctl -n hw.ncpu)" --target blas lapack
cp build-arm64/lib/libblas.a "$MAD_BIN/librefblas.a"; cp build-arm64/lib/liblapack.a "$MAD_BIN"

# NFFT
cd "$MAD_DEPS/nfft-3.5.3" && CC="$CC" CFLAGS='-O3 -fPIC' ./configure --enable-all --disable-shared --with-fftw3="$MAD_DEPS/fftw-3.3.10" --with-fftw3-libdir="$MAD_DEPS/fftw-3.3.10/.libs" --with-fftw3-includedir="$MAD_DEPS/fftw-3.3.10/api" && make -j"$(sysctl -n hw.ncpu)"
cp .libs/libnfft3.a "$MAD_BIN"
```

## Verify and build MAD

```sh
lipo -info "$MAD_BIN"/*.a       # every archive must say arm64
cd "$MAD_ROOT/src"
make -f Makefile.macosx clean
make -f Makefile.macosx CC="$CC" CXX="$CXX" FC="$FC" LIB="$MAD_DEPS"
lipo -info mad
```

`Makefile.macosx` skips the x86-only SSE/AVX source on Apple Silicon and
rejects a non-arm64 archive before linking.
