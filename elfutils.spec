# based on PLD Linux spec git://git.pld-linux.org/packages/elfutils.git
Summary:	A collection of utilities and DSOs to handle compiled objects
Name:		elfutils
Version:	0.159
Release:	2
License:	GPL v2 with OSL linking exception
Group:		Development/Tools
Source0:	https://fedorahosted.org/releases/e/l/elfutils/%{version}/%{name}-%{version}.tar.bz2
# Source0-md5:	1f45a18231c782ccd0966059e2e42ea9
Patch0:		%{name}-debian-manpages.patch
URL:		https://fedorahosted.org/elfutils/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	gettext
BuildRequires:	libltdl-devel
BuildRequires:	perl-tools-pod
Requires:	%{name}-libelf = %{version}-%{release}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

# fails to build with -Wl,-s
%define		filterout_ld	(-Wl,)?-[sS] (-Wl,)?--strip.*
%define		_programprefix	eu-

%description
Elfutils is a collection of utilities, including ld (a linker), nm
(for listing symbols from object files), size (for listing the section
sizes of an object or archive file), strip (for discarding symbols),
readline (the see the raw ELF file structures), and elflint (to check
for well-formed ELF files). Also included are numerous helper
libraries which implement DWARF, ELF, and machine-specific ELF
handling.

%package devel
Summary:	Development part of libraries to handle compiled objects
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
The elfutils-devel package contains the development part of libraries
to create applications for handling compiled objects. libelf allows
you to access the internals of the ELF object file format, so you can
see the different sections of an ELF file. libebl provides some
higher-level ELF access functionality. libdwarf provides access to the
DWARF debugging information. libasm provides a programmable assembler
interface.

%package static
Summary:	Static libraries
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static libraries.

%package libelf
Summary:	Library to read and write ELF files
Group:		Libraries

%description libelf
The elfutils-libelf package provides a DSO which allows reading and
writing ELF files on a high level. Third party programs depend on this
package to read internals of ELF files. The programs of the elfutils
package use it also to generate new ELF files.

%prep
%setup -q
%patch0 -p1

%build
%{__libtoolize}
%{__aclocal} -I m4
%{__autoheader}
%{__automake}
%{__autoconf}

bash %configure \
	--enable-shared \
	--program-prefix=%{_programprefix} \

# make check depends on test-nlist not stripped
%{__perl} -pi -e 's/^(LDFLAGS =.*)-s/$1/' tests/Makefile

%{__make}
%{__make} -C debian/man

%check
LC_ALL=C %{__make} -C tests check

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_mandir}/man1,/%{_lib}}

# *OBJEXT must be passed to workaround problem with messed gettext,
# which doesn't like *-po dir names
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	MKINSTALLDIRS=$(pwd)/config/mkinstalldirs \
	CATOBJEXT=.gmo \
	INSTOBJEXT=.mo

install debian/man/*.1 $RPM_BUILD_ROOT%{_mandir}/man1

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /usr/sbin/ldconfig
%postun	-p /usr/sbin/ldconfig

%post	libelf -p /usr/sbin/ldconfig
%postun	libelf -p /usr/sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc AUTHORS COPYING NEWS NOTES README THANKS TODO
%attr(755,root,root) %{_bindir}/*
%attr(755,root,root) %{_libdir}/elfutils/lib*.so
%attr(755,root,root) %ghost %{_libdir}/libasm.so.?
%attr(755,root,root) %ghost %{_libdir}/libdw.so.?
%attr(755,root,root) %{_libdir}/libasm-*.so
%attr(755,root,root) %{_libdir}/libdw-*.so
%dir %{_libdir}/elfutils
%{_mandir}/man1/*.1*

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libasm.so
%attr(755,root,root) %{_libdir}/libdw.so
%attr(755,root,root) %{_libdir}/libelf.so
%{_libdir}/libebl.a
%{_includedir}/*

%files libelf
%defattr(644,root,root,755)
%attr(755,root,root) %ghost %{_libdir}/libelf.so.?
%attr(755,root,root) %{_libdir}/libelf-*.so

%files static
%defattr(644,root,root,755)
%{_libdir}/libasm.a
%{_libdir}/libdw.a
%{_libdir}/libelf.a

