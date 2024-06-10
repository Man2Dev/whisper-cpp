# Pass "--with=exmaples" to rpmbuild if you want the examples
%bcond_with examples
# Pass "--with=tests" to rpmbuild if you want to run the tests
%bcond_with tests
# Pass --without=devel to rpmbuild if you don't want to run the devel
%bcond_without devel

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

ExclusiveArch:  x86_64 aarch64 ppc64le
%global toolchain clang

BuildRequires:  cmake
BuildRequires:  clang

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

%if %{with devel}
%package devel
Summary:        Libraries, headers, tests and examples for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
%{summary}
%endif

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

%prep
%autosetup -p1 -n whisper.cpp-%{version}

# verson the *.so
sed -i -e 's/POSITION_INDEPENDENT_CODE ON/POSITION_INDEPENDENT_CODE ON SOVERSION %{version}/' CMakeLists.txt

%build

%cmake \
    -DWHISPER_NO_AVX=ON \
    -DWHISPER_NO_AVX2=ON \
    -DWHISPER_NO_FMA=ON \
    -DWHISPER_NO_F16C=ON \
%if %{with devel}
    -DWHISPER_BUILD_EXAMPLES=ON \
    -DWHISPER_BUILD_TESTS=ON \
%else
    -DWHISPER_BUILD_TESTS=OFF \
    -DWHISPER_BUILD_EXAMPLES=OFF \
%endif
%if %{with examples}
    -DWHISPER_BUILD_EXAMPLES=ON \
%endif
%if %{with test}
    -DWHISPER_BUILD_TESTS=ON
%endif

%cmake_build

%install
%cmake_install

%check
%ctest

%files
%license LICENSE
%{_libdir}/libwhisper.so.%{version}

%files devel
%doc AUTHORS
%doc README.md
%license LICENSE
%{_includedir}/ggml.h
%{_includedir}/whisper.h
%{_libdir}/libwhisper.so

%changelog
%autochangelog

