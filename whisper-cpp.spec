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
# Patch0:         0001-Gieneralize-install-locations.patch

ExclusiveArch:  x86_64 aarch64
%global toolchain gcc

BuildRequires:  cmake >= 3.27
BuildRequires:  clang
BuildRequires:  coreutils
BuildRequires:  git
BuildRequires:  ccache
# BuildRequires:  ffmpeg-free-devel
BuildRequires:  pkgconfig(libavcodec)
BuildRequires:  pkgconfig(libavformat)
BuildRequires:  pkgconfig(libavdevice)
BuildRequires:  pkgconfig(libavutil)
BuildRequires:  pkgconfig(libavfilter)
BuildRequires:  pkgconfig(libswscale)
BuildRequires:  pkgconfig(libpostproc)
BuildRequires:  pkgconfig(libswresample)

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
%autosetup -n whisper.cpp-%{version}

# verson the *.so
sed -i -e 's/POSITION_INDEPENDENT_CODE ON/POSITION_INDEPENDENT_CODE ON SOVERSION %{version}/' CMakeLists.txt

# git cruft
find . -name '.gitignore' -exec rm -rf {} \;

%build
# export TARGET=%{buildroot}
%cmake \
    -DCMAKE_SYSTEM_PROCESSOR=%{_build_cpu} \
    -DCMAKE_SYSTEM_NAME="Linux" \
    -DBUILD_SHARED_LIBS_DEFAULT=OFF \
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
%else
    -DWHISPER_OPENVINO=OFF \
%endif
%if %{with openblas}
    -DWHISPER_OPENBLAS=ON \
%else
    -DWHISPER_OPENBLAS=OFF \
%endif
%if %{with examples}
    -DWHISPER_BUILD_EXAMPLES=ON \
%else
    -DWHISPER_BUILD_EXAMPLES=OFF \
%endif
%if %{with test}
    -DWHISPER_BUILD_TESTS=ON \
%else
    -DWHISPER_BUILD_TESTS=OFF \
%endif

%make_build

%install
%make_install %{__make} install DESTDIR=%{?buildroot} \
     INSTALL="%{__install} -Dp %{_vpath_srcdir}/main -t %{buildroot}%{_bindir}/whisper-cpp" \
     INSTALL="%{__install} -Dp %{_vpath_srcdir}/quantize -t %{buildroot}%{_bindir}/whisper-cpp-quantize" \
     INSTALL="%{__install} -Dp %{_vpath_srcdir}/server -t %{buildroot}%{_bindir}/whisper-cpp-server" \
     INSTALL="%{__install} -Dp %{_vpath_srcdir}/bench -t %{buildroot}%{_bindir}/whisper-cpp-bench" \
     INSTALL="%{__install} -Dp %{_vpath_srcdir}/main -t %{buildroot}%{_libdir}/main" \
     INSTALL="%{__install} -Dp %{_vpath_srcdir}/quantize -t %{buildroot}%{_libdir}/quantize" \
     INSTALL="%{__install} -Dp %{_vpath_srcdir}/server -t %{buildroot}%{_libdir}/server" \
     INSTALL="%{__install} -Dp %{_vpath_srcdir}/bench -t %{buildroot}%{_libdir}/bench" \
     INSTALL="%{__install} -Dp %{_vpath_srcdir}/ggml-alloc.o -t %{buildroot}%{_libdir}/ggml-alloc.o" \
     INSTALL="%{__install} -Dp %{_vpath_srcdir}/ggml-backend.o -t %{buildroot}%{_libdir}/ggml-backend.o" \
     INSTALL="%{__install} -Dp %{_vpath_srcdir}/ggml.o -t %{buildroot}%{_libdir}/ggml.o" \
     INSTALL="%{__install} -Dp %{_vpath_srcdir}/ggml-quants.o -t %{buildroot}%{_libdir}/ggml-quants.o" \
     INSTALL="%{__install} -Dp %{_vpath_srcdir}/whisper.o -t %{buildroot}%{_libdir}/whisper.o" \

%files
%doc README.md
%doc AUTHORS
%license LICENSE
%{_bindir}/whisper-cpp
%{_bindir}/whisper-cpp-quantize
%{_bindir}/whisper-cpp-server
%{_bindir}/whisper-cpp-bench

%files devel
%doc README.md
%license LICENSE
%{_libdir}/main
%{_libdir}/quantize
%{_libdir}/server
%{_libdir}/bench
%{_libdir}/ggml-alloc.o
%{_libdir}/ggml-backend.o
%{_libdir}/ggml.o
%{_libdir}/ggml-quants.o
%{_libdir}/whisper.o

%changelog
%autochangelog

