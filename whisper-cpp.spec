# Some optional subpackages
%bcond_with examples
%bcond_with test
%bcond_with openblas
%bcond_with openvino

Summary:        Port of OpenAI's Whisper model in C/C++
Name:           whisper-cpp

License:        MIT
# Some execptions
# Apache-2
# bindings/java/gradlew*
# examples/whisper.android/gradlew*
# These are not distributed

Version:        1.6.2
Release:        %autorelease

URL:            https://github.com/ggerganov/whisper.cpp
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/whisper.cpp-%{version}.tar.gz
# https://github.com/ggerganov/whisper.cpp/pull/1791
Patch0:         0001-Generalize-install-locations.patch

ExclusiveArch:  x86_64 aarch64
%global toolchain gcc

BuildRequires:  cmake >= 3.27
BuildRequires:  clang
BuildRequires:  coreutils
BuildRequires:  git
BuildRequires:  ccache
BuildRequires:  SDL2-static
# BuildRequires:  ffmpeg-free-devel
BuildRequires:  pkgconfig(libavcodec)
BuildRequires:  pkgconfig(libavformat)
BuildRequires:  pkgconfig(libavdevice)
BuildRequires:  pkgconfig(libavutil)
BuildRequires:  pkgconfig(libavfilter)
BuildRequires:  pkgconfig(libswscale)
BuildRequires:  pkgconfig(libpostproc)
BuildRequires:  pkgconfig(libswresample)
BuildRequires:  python3-devel
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(poetry)

Requires:  /usr/bin/ffmpeg
Requires:  pkgconfig(libavcodec)
Requires:  pkgconfig(libavformat)
Requires:  pkgconfig(libavdevice)
Requires:  pkgconfig(libavutil)
Requires:  pkgconfig(libavfilter)
Requires:  pkgconfig(libswscale)
Requires:  pkgconfig(libpostproc)
Requires:  pkgconfig(libswresample)

# TODO: add openblas package
# TODO: add OPENVINO package
# TODO: add CLBLAST package

# TODO opencl, rocm, CoreML
# TODO bindings/go/* and add package


%global base_description \
High-performance inference of OpenAI's Whisper automatic speech \
recognition (ASR) model: \
	\
* Plain C/C++ implementation without dependencies \
* Apple Silicon first-class citizen - optimized via ARM NEON, \
*  Accelerate framework, Metal and Core ML \
* AVX intrinsics support for x86 architectures \
* VSX intrinsics support for POWER architectures \
* Mixed F16 / F32 precision \
* 4-bit and 5-bit integer quantization support \
* Zero memory allocations at runtime \
* Support for CPU-only inference \
* Efficient GPU support for NVIDIA \
* Partial OpenCL GPU support via CLBlast \
* OpenVINO Support \
* C-style API

%description
%{base_description}

%package devel
Summary:        Libraries and headers for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
%{base_description}

%if %{with test}
%package test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description test
%{summary}
%endif

%if %{with examples}
%package examples
Summary:        Examples for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description examples
%{summary}
%endif

%if %{with openvino}
%package openvino
Summary:        %{name} with openvino
Requires:       %{name}%{?_isa} = openvino-%{version}-%{release}

%description openvino
%{summary}
%endif

%if %{with openblas}
%package openblas
Summary:        %{name} with openblas
Requires:       %{name}%{?_isa} = openblas-%{version}-%{release}

%description openblas
%{summary}
%endif

%prep
%autosetup -p1 -n whisper.cpp-%{version}

# verson the *.so
sed -i -e 's/POSITION_INDEPENDENT_CODE ON/POSITION_INDEPENDENT_CODE ON SOVERSION %{version}/' CMakeLists.txt

# git cruft
find . -name '.gitignore' -exec rm -rf {} \;

%build
make clean

%set_build_flags \
  CFLAGS="${CFLAGS:-%{?build_cflags}}" ; export CFLAGS ; \
  CXXFLAGS="${CXXFLAGS:-%{?build_cxxflags}}" ; export CXXFLAGS ; \
  FFLAGS="${FFLAGS:-%{?build_fflags}}" ; export FFLAGS ; \
  FCFLAGS="${FCFLAGS:-%{?build_fflags}}" ; export FCFLAGS ; \
  LDFLAGS="${LDFLAGS:-%{?build_ldflags}}" ; export LDFLAGS

%cmake \
    -DCMAKE_BUILD_TYPE="RelWithDebInfo" \
    -DINCLUDE_INSTALL_DIR=%{_includedir} \
    -DLIB_INSTALL_DIR=%{_libdir} \
    -DLIB_SUFFIX=".so" \
    -DSHARE_INSTALL_PREFIX=%{_prefix} \
    -DSYSCONF_INSTALL_DIR=%{_sysconfdir} \
    -DCMAKE_SYSTEM_PROCESSOR=%{_build_cpu} \
    -DCMAKE_SYSTEM_NAME="Linux" \
    -DBUILD_SHARED_LIBS_DEFAULT=ON \
    -DWHISPER_WASM_SINGLE_FILE=OFF \
    -DWHISPER_ALL_WARNINGS_3RD_PARTY=ON \
    -DWHISPER_SANITIZE_THREAD=OFF \
    -DWHISPER_SANITIZE_ADDRESS=OFF \
    -DWHISPER_SANITIZE_UNDEFINED=OFF \
    -DWHISPER_BUILD_TESTS=OFF \
    -DWHISPER_BUILD_EXAMPLES=OFF \
    -DWHISPER_SDL2=ON \
    -DWHISPER_FFMPEG=ON \
    -DWHISPER_NO_AVX2=OFF \
    -DWHISPER_NO_AVX512=OFF \
    -DWHISPER_NO_AVX512_VBMI=OFF \
    -DWHISPER_NO_AVX512_VNNI=OFF \
    -DWHISPER_NO_FMA=OFF \
    -DWHISPER_NO_F16C=OFF \
    -DWHISPER_PERF=OFF \
%if %{with openvino}
    -DWHISPER_OPENVINO=ON \
%endif
%if %{with openblas}
    -DWHISPER_OPENBLAS=ON \
%endif
%if %{with examples}
    -DWHISPER_BUILD_EXAMPLES=ON \
%endif
%if %{with test}
    -DWHISPER_BUILD_TESTS=ON \
%endif


# output:
# main, quantize, server, bench
%make_build
# stream
%make_build stream
# libwhisper.so libwhisper.so.%{version}
%cmake_build

# built files moved to redhat-linux-build
cp -p %{_vpath_srcdir}/main redhat-linux-build/main
cp -p %{_vpath_srcdir}/quantize redhat-linux-build/quantize
cp -p %{_vpath_srcdir}/server redhat-linux-build/server
cp -p %{_vpath_srcdir}/bench redhat-linux-build/bench
cp -p %{_vpath_srcdir}/stream redhat-linux-build/stream
cp -p %{_vpath_srcdir}/ggml-alloc.o redhat-linux-build/ggml-alloc.o
cp -p %{_vpath_srcdir}/ggml-backend.o redhat-linux-build/ggml-backend.o
cp -p %{_vpath_srcdir}/ggml.o redhat-linux-build/ggml.o
cp -p %{_vpath_srcdir}/ggml-quants.o redhat-linux-build/ggml-quants.o
cp -p %{_vpath_srcdir}/whisper.o redhat-linux-build/whisper.o

cp -p %{_vpath_srcdir}/main redhat-linux-build/whisper-cpp
cp -p %{_vpath_srcdir}/quantize redhat-linux-build/whisper-cpp-quantize
cp -p %{_vpath_srcdir}/server redhat-linux-build/whisper-cpp-server
cp -p %{_vpath_srcdir}/bench redhat-linux-build/whisper-cpp-bench
cp -p %{_vpath_srcdir}/stream redhat-linux-build/whisper-cpp-stream

%install
%cmake_install

%files
%doc README.md
%doc AUTHORS
%license LICENSE
%{_bindir}/whisper-cpp
%{_bindir}/whisper-cpp-quantize
%{_bindir}/whisper-cpp-server
%{_bindir}/whisper-cpp-bench
%{_bindir}/whisper-cpp-stream
%{_libdir}/libwhisper.so.%{version}

%files devel
%doc README.md
%license LICENSE
%{_libdir}/main
%{_libdir}/quantize
%{_libdir}/server
%{_libdir}/bench
%{_libdir}/stream
%{_libdir}/ggml-alloc.o
%{_libdir}/ggml-backend.o
%{_libdir}/ggml.o
%{_libdir}/ggml-quants.o
%{_includedir}/ggml.h
%{_includedir}/whisper.h
%{_libdir}/whisper.o
%{_libdir}/libwhisper.so

%changelog
%autochangelog

