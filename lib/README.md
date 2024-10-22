# The guide to building all the libraries for MAD-NG using a CERN Computer (RPM based)
To ensure that all the libraries are built correctly, you should be in the `lib` directory.  (If you are not, you can change to the `lib` directory by running `cd lib`.)

This guide will help you build all the libraries required for MAD-NG.

## Prerequisites
Before you start, you need to have initialised all the submodules. If you have not done this, you can do this by running the following command:
```bash
git submodule update --init --recursive
```

This can be run from any directory in the MAD-NG repository and ensures that all the submodules are correctly initialised, of which the bin directory is the most important. You should now see the `bin` has been populated with a `linux` and `macosx` directory, along with a `LICENSE` file.

### Install the gfortran compiler
```bash
sudo yum install gcc-toolset-12
```
If at the end, you get an error message relating to /usr/bin/ld, you can try to enable the toolset by running:
```bash
scl enable gcc-toolset-12 bash
```
If this works, you may want to add a file in /etc/profile.d/ with the following content:
```bash
#!/bin/bash
source scl_source enable gcc-toolset-12
```

## Luajit

### Retrieve the source code from the repository
This code does the following:
1. Clones the repository from the a fork of the LuaJIT repository, naming the directory `luajit`.
2. Changes the directory to the `luajit` directory.
3. Checks out the `mad-patch` branch. (This should be the default branch.)
4. Pulls the latest changes from the repository. (This should be redundant, but it is included for completeness.)

```bash
git clone https://github.com/MethodicalAcceleratorDesign/LuaJIT.git/ luajit
cd luajit ; git checkout mad-patch ; git pull
```

### Build the library
We assume that you are in still in the `luajit` directory from the previous step.

```bash
make clean
make amalg PREFIX=`pwd`
make install PREFIX=`pwd`
mv bin/luajit-2.1.0-beta3 bin/luajit
cp src/libluajit.a ../../bin/linux
```
or in one line:
```bash
make clean ; make amalg PREFIX=`pwd` ; make install PREFIX=`pwd` ; mv bin/luajit-2.1.0-beta3 bin/luajit ; cp src/libluajit.a ../../bin/linux/
```

This code does the following:
1. Cleans the build directory.
2. Builds the library.
3. Installs the library.
4. Changes the name of the binary to `luajit`.
5. Copies the library to the `bin/linux` directory in the MAD-NG repository. This is the directory where the MAD-NG executable will look for all the libraries.

## FFTW3
To begin this step, I assume that you are in the `lib` directory, if you are still in the `luajit` directory, you can change to the `lib` directory by running:
```bash
cd ..
```

### Retrieve the source code from a tarball
```bash
wget ftp://ftp.fftw.org/pub/fftw/fftw-3.3.10.tar.gz
mkdir fftw3
tar xvzf fftw-3.3.10.tar.gz -C fftw3 --strip-components=1
```

Line-by-line:
1. Downloads the FFTW3 source code.
2. Creates the `fftw3` directory.
3. Extracts the source code to the `fftw3` directory.

### Build the library
```bash
cd fftw3
./configure --disable-shared
make
cp .libs/libfftw3.a ../../bin/linux
```

Line-by-line:
1. Changes the directory to the `fftw3` directory.
2. Configures the build to disable shared libraries.
3. Builds the library.
4. Copies the built library to the `bin/linux` directory in the MAD-NG repository.

## NFFT3
To begin this step, I assume that you are in the `lib` directory, if you are still in the `fftw3` directory, you can change to the `lib` directory by running:
```bash
cd ..
```

### Retrieve the source code from a tarball
```bash
wget http://www.nfft.org/download/nfft-3.5.1.tar.gz
mkdir nfft3
tar xvzf nfft-3.5.1.tar.gz -C nfft3 --strip-components=1
``` 

### Build the library
See https://www-user.tu-chemnitz.de/~potts/nfft/installation.php for more information.
```bash
cd nfft3
./configure --enable-all --disable-shared \
            --with-fftw3=`pwd`/../fftw3 \
            --with-fftw3-libdir=`pwd`/../fftw3/.libs \
            --with-fftw3-includedir=`pwd`/../fftw3/api
make
cp .libs/libnfft3.a ../../bin/linux
```

Line-by-line:
1. Changes the directory to the `nfft3` directory.
2. Configures the build to enable all options and disable shared libraries.
3. Builds the library.
4. Copies the built library to the `bin/linux` directory in the MAD-NG repository.

## nlopt
Again, make sure you are in the `lib` directory before you start this step.

### Retrieve the source code from the github repository and build the library
```bash
git clone https://github.com/stevengj/nlopt.git
cd nlopt ; mkdir build ; cd build
cmake -DNLOPT_GUILE=OFF -DNLOPT_MATLAB=OFF -DNLOPT_OCTAVE=OFF -DNLOPT_PYTHON=OFF -DNLOPT_SWIG=OFF -DNLOPT_CXX=OFF -DNLOPT_FORTRAN=OFF -DBUILD_SHARED_LIBS=OFF ..
make
cp ./libnlopt.a ../../../bin/linux
```

## lapack
Again, make sure you are in the `lib` directory before you start this step. (If you have not changed directory, since the nlopt step, you can run `cd ../../` to change to the `lib` directory.)

### Retrieve the source code from the github repository and build the library
```bash
git clone https://github.com/Reference-LAPACK/lapack.git
cd lapack ; git pull
cp make.inc.example make.inc
```

Edit the `make.inc` file as follows:
```diff
- CFLAGS = -O3
+ CFLAGS = -O3 -fpic
```
```diff
- FFLAGS = -O2 -frecursive
+ FFLAGS = -O2 -frecursive -fpic
```
```diff
- FFLAGS_NOOPT = -O0 -frecursive
+ FFLAGS_NOOPT = -O0 -frecursive -fpic
```

Edit the `Makefile` file as follows (select lib: blaslib ...):
```diff
- lib: lapacklib tmglib
+ # lib: lapacklib tmglib
- #lib: blaslib variants lapacklib tmglib
+ lib: blaslib variants lapacklib tmglib
```

Finally, build the library:
```bash
make clean ; make lib ; make blas_testing lapack_testing
cp liblapack.a librefblas.a ../../bin/linux
```

## lpeg
Again, make sure you are in the `lib` directory before you start this step. (If you have not changed directory, since the lapack step, you can run `cd ../` to change to the `lib` directory.)

### Retrieve the source code from a tarball
```bash
wget http://www.inf.puc-rio.br/~roberto/lpeg/lpeg-1.0.2.tar.gz
mkdir lpeg
tar xvzf lpeg-1.0.2.tar.gz -C lpeg --strip-components=1
```

Please note, that this did not work for me, as I got the following error:
```
ERROR: The certificate of 'www.inf.puc-rio.br' is not trusted.
ERROR: The certificate of 'www.inf.puc-rio.br' doesn't have a known issuer.
```
So you can just download the file by entering the URL in your browser and then move it to the `lib` directory.

### Build the library
```bash
cd lpeg
```

Edit the `makefile` file as follows:
```diff
- LUADIR = ../lua/
+ #LUADIR = ../lua/
+ LUADIR = ../luajit/include/luajit-2.1
+ LUALIB = ../luajit/lib/libluajit-5.1.a
```
```diff
- COPT = -O2 -DNDEBUG
+ COPT = -O3
```
In the below diff, take care to ensure that the indentation is correct, i.e. the `+ ` take up some space for the correct indentation.
```diff
# For Linux
linux:
-	$(MAKE) lpeg.so "DLLFLAGS = -shared -fPIC"
+	$(MAKE) lpeg.a "DLLFLAGS = -shared -fPIC"

macosx:
-	$(MAKE) lpeg.so "DLLFLAGS = -bundle -undefined dynamic_lookup"
+	$(MAKE) lpeg.a "DLLFLAGS = -bundle -undefined dynamic_lookup"
+
+ lpeg.a: $(FILES)
+   env $(AR) -r lib$@ $(FILES)

lpeg.so: $(FILES)
	  env $(CC) $(DLLFLAGS) $(FILES) -o lpeg.so
```
```diff
clean:
-	rm -f $(FILES) lpeg.so
+	rm -f $(FILES) lpeg.so lpeg.a
```

Finally, build the library:
```bash
make linux
cp liblpeg.a ../../bin/linux
```

### Copy re.lua
Open the re.lua file and make the following changes:
```diff
- return re
+ -- return re
+ return { regex = re } -- MAD
```
Then copy the file to the `src` directory:
```bash
cp re.lua ../../src/madl_regex.lua
```

## lfs
Again, make sure you are in the `lib` directory before you start this step. (If you have not changed directory, since the lpeg step, you can run `cd ../` to change to the `lib` directory.)

### Retrieve the source code from GitHub and build the library
```bash
git clone https://github.com/MethodicalAcceleratorDesign/luafilesystem.git lfs
cd lfs
make lfs.a
cp liblfs.a ../../bin/linux
```