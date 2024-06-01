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
#BuildRequires:  ffmpeg
#BuildRequires:  ffmpeg-devel

Requires:	ffmpeg
Requires:	ffmpeg-devel

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
%cmake \
%ifarch x86_64
    -DCMAKE_SYSTEM_ARCHITECTURE=%{_build_cpu}
%endif
%ifarch aarch64
    -DCMAKE_SYSTEM_ARCHITECTURE=%{_build_cpu}
%endif
    -DCMAKE_SYSTEM_NAME="Linux" \
    -DCMAKE_BUILD_TYPE="Release" \
    -DBUILD_SHARED_LIBS_DEFAULT=ON \
    -DWHISPER_WASM_SINGLE_FILE=OFF \
    -DWHISPER_ALL_WARNINGS_3RD_PARTY=ON \
    -DWHISPER_SANITIZE_THREAD=OFF \
    -DWHISPER_SANITIZE_ADDRESS=OFF \
    -DWHISPER_SANITIZE_UNDEFINED=OFF \
    -DCMAKE_SYSTEM_NAME=ON
    -DWHISPER_BUILD_TESTS=OFF \
    -DWHISPER_BUILD_EXAMPLES=OFF \
    -DWHISPER_SDL2=OFF \
    -DWHISPER_FFMPEG=ON \
    -DWHISPER_NO_AVX=ON \
    -DWHISPER_NO_AVX2=ON \
    -DWHISPER_NO_AVX512=ON \
    -DWHISPER_NO_AVX512_VBMI=ON \
    -DWHISPER_NO_AVX512_VNNI=ON \
    -DWHISPER_NO_FMA=ON \
    -DWHISPER_NO_F16C=ON \
    -DWHISPER_PERF=OFF
%if %{with openvino}
    -DWHISPER_OPENVINO=ON
%else
    -DWHISPER_OPENVINO=OFF
%endif
%if %{with openblas}
    -DWHISPER_OPENBLAS=ON
%else
    -DWHISPER_OPENBLAS=OFF
%endif
%if %{with examples}
    -DWHISPER_BUILD_EXAMPLES=ON
%else
    -DWHISPER_BUILD_EXAMPLES=OFF
%endif
%if %{with test}
    -DWHISPER_BUILD_TESTS=OFF
%else
    -DWHISPER_BUILD_TESTS=OFF
%endif

%make_build

%install
%make_install

%check
%ctest

%files
%license LICENSE
%{_libdir}/libwhisper.so.%{version}

%files devel
%doc README.md
%{_includedir}/ggml.h
%{_includedir}/whisper.h
%{_libdir}/libwhisper.so

%changelog
%autochangelog

