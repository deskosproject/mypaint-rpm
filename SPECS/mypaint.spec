%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

Name:           mypaint
Version:        1.1.0
Release:        1%{?dist}
Summary:        A fast and easy graphics application for digital painters

Group:          Applications/Multimedia
# MyPaint is GPLv2+, brush library LGPLv2+
# Ramon and CD_concept brushes are CC-BY
License:        GPLv2+ and LGPLv2+ and CC-BY
URL:            http://mypaint.intilinux.com/
Source0:        http://download.gna.org/mypaint/%{name}-%{version}.tar.bz2
Source1:        http://mypaintatelier.googlecode.com/files/ramon2.zip
# taken from http://mypaintatelier.googlecode.com/files/Concept%20Design.zip
# but koji doesn't like sources with a whitespace, so we rename it
Source2:        Concept_Design.zip
# don't allow a prefix of "/" and assum a prefix of "/usr" instead
# occurs with a usrmoved system
Patch0:         mypaint-1.0.0-usrmove.patch
# Upstream bug: https://gna.org/bugs/?20754
# Upstream fix: https://gitorious.org/mypaint/mypaint/commit/c006e4e
Patch1:         mypaint-1.1.0-scons.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  python-devel, gtk2-devel, pygtk2-devel
BuildRequires:  json-c-devel
BuildRequires:  protobuf-devel
BuildRequires:  lcms2-devel
BuildRequires:  numpy, scons, swig
BuildRequires:  desktop-file-utils, gettext, intltool
Requires:       gtk2, numpy, pygtk2, python, protobuf-python
Requires:       %{name}-data = %{version}-%{release}

%description
MyPaint is a fast and easy graphics application for digital painters. It lets 
you focus on the art instead of the program. You work on your canvas with 
minimum distractions, bringing up the interface only when you need it.


%package        data
Summary:        Common data files for for %{name}
Requires:       %{name} = %{version}-%{release}
BuildArch:      noarch

%description    data
The %{name}-data package contains common data files for %{name}.


%package        devel
Summary:        Development files for %{name}
Group:          Development/Libraries
Requires:       %{name} = %{version}-%{release}

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%prep
%setup -q
%patch0 -p1 -b .usrmove
%patch1 -p1 -b .scons

# Ramon2 brushes
unzip %{SOURCE1} -x order.conf -d brushes
unzip -p %{SOURCE1} order.conf >> brushes/order.conf
mv brushes/readme.txt README.Ramon2

# Concept Design brushes
unzip %{SOURCE2} -x order.conf -d brushes
unzip -p %{SOURCE2} order.conf >> brushes/order.conf
mv brushes/readme.txt README.CD_concept

# the Options class is deprecated; use the Variables class instead
sed -i 's|PathOption|PathVariable|g' SConstruct
sed -i 's|Options|Variables|g' SConstruct

# for 64 bit
sed -i 's|lib/mypaint|%{_lib}/mypaint|g' SConscript SConstruct mypaint.py
sed -i 's|lib/pkgconfig|%{_lib}/pkgconfig|g' SConscript brushlib/SConscript

# fix menu icon
sed -i 's|mypaint_48|mypaint|g' desktop/%{name}.desktop


%build
export CFLAGS="$RPM_OPT_FLAGS"
export CXXFLAGS="$RPM_OPT_FLAGS"
scons prefix=%{_prefix} %{?_smp_mflags}


%install
rm -rf %{buildroot}
scons prefix=%{buildroot}%{_prefix} install

desktop-file-install \
%if 0%{?fedora} && 0%{?fedora} < 19
  --vendor="fedora" \
%endif
  --delete-original \
  --remove-key="Encoding" \
  --dir=%{buildroot}%{_datadir}/applications \
   %{buildroot}%{_datadir}/applications/%{name}.desktop

# the SConscript is dumb and includes %%{buildroot}. Let's just strip it here.
sed -i 's|%{buildroot}||' %{buildroot}%{_libdir}/pkgconfig/libmypaint.pc

find %{buildroot} -name '*.la' -exec rm -f {} ';'
find %{buildroot} -name '*.a' -exec rm -f {} ';'

chmod 755 %{buildroot}%{_libdir}/mypaint/_mypaintlib.so

%find_lang %{name}
%find_lang libmypaint


%clean
rm -rf %{buildroot}


%post data
touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
update-desktop-database &> /dev/null || :


%postun data
if [ $1 -eq 0 ] ; then
    touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi
update-desktop-database &> /dev/null || :


%posttrans data
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :


%files -f %{name}.lang -f libmypaint.lang
%defattr(-,root,root,-)
%doc changelog COPYING LICENSE README README.CD_concept README.Ramon2 doc/
%{_bindir}/%{name}
%dir %{_libdir}/mypaint/
%{_libdir}/mypaint/_mypaintlib.so

%files data
%defattr(-,root,root,-)
%{_datadir}/%{name}/
%if 0%{?fedora} && 0%{?fedora} < 19
%{_datadir}/applications/fedora-%{name}.desktop
%else
%{_datadir}/applications/%{name}.desktop
%endif
%{_datadir}/icons/hicolor/*/*/*


%files devel
%defattr(-,root,root,-)
%doc
%{_includedir}/*
%{_libdir}/pkgconfig/libmypaint.pc

%changelog
* Tue Aug 13 2013 Christoph Wickert <cwickert@fedoraproject.org> - 1.1.0-1
- Update to 1.1.0 (#891044)
- New devel package to develop brushlibs
- Add patch to make mypaint honor compiler flags
- Move more files over to mypaint-data package to save more space on mirrors
- Make sure scriptlets are called for the right subpackage

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.0-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Thu Feb 14 2013 Toshio Kuratomi <toshio@fedoraproject.org> - 1.0.0-7
- Remove --vendor from desktop-file-install https://fedorahosted.org/fesco/ticket/1077

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Fri Jan 04 2013 Christoph Wickert <cwickert@fedoraproject.org> - 1.0.0-5
- Rebuild against numpy 1.7 (fixes 4837925)

* Wed Sep 26 2012 Thomas Spura <tomspur@fedoraproject.org> - 1.0.0-4
- patch: assume a prefix of /usr instead of / in a usrmoved system (fixes #797263)

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.0.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Jan 10 2012 Christoph Wickert <cwickert@fedoraproject.org> - 1.0.0-2
- %%{_bindir}/mypaint is arch specific and belongs into base package (#773079)

* Tue Jan 10 2012 Christoph Wickert <cwickert@fedoraproject.org> - 1.0.0-1
- Update to 1.0.0
- Add brush sets Ramon2 and Concept Design

* Tue Dec 06 2011 Adam Jackson <ajax@redhat.com> - 0.9.1-2
- Rebuild for new libpng

* Sat Mar 05 2011 Christoph Wickert <cwickert@fedoraproject.org> - 0.9.1-1
- Update to 0.9.1

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.8.2-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Wed Aug 11 2010 David Malcolm <dmalcolm@redhat.com> - 0.8.2-4
- recompiling .py files against Python 2.7 (rhbz#623339)

* Wed Aug 11 2010 Christoph Wickert <cwickert@fedoraproject.org> - 0.8.2-3
- Rebuild for Python 2.7 (#623339)
 
* Fri Apr 16 2010 Christoph Wickert <cwickert@fedoraproject.org> - 0.8-2-2
- Rebuild (fixes 583156)

* Mon Mar 01 2010 Christoph Wickert <cwickert@fedoraproject.org> - 0.8.2-1
- Update to 0.8.2

* Sun Feb 21 2010 Christoph Wickert <cwickert@fedoraproject.org> - 0.8.1-1
- Update to 0.8.1

* Fri Jan 29 2010 Christoph Wickert <cwickert@fedoraproject.org> - 0.8.0-1
- Update to 0.8.0

* Sat Nov 28 2009 Christoph Wickert <cwickert@fedoraproject.org> - 0.7.1-2
- Require numpy

* Wed Nov 25 2009 Christoph Wickert <cwickert@fedoraproject.org> - 0.7.1-1
- Update to 0.7.1
- Move private python modules to a private location
- Add scriptlets for gtk-update-icon-cache and update-desktop-database
- Fix License and Source0 tags

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.5.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.5.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 0.5.1-3
- Rebuild for Python 2.6

* Mon Nov 3 2008 Marc Wiriadisastra <marc@mwiriadi.id.au> - 0.5.1-2
- Add new website and download link
- Fix mydrawwidget location for F-10

* Sun Jul 27 2008 Marc Wiriadisastra <marc@mwiriadi.id.au> - 0.5.1-1
- New version

* Wed Feb 13 2008 Marc Wiriadisastra <marc@mwiriadi.id.au> - 0.5.0-7
- Rebuild for gcc4.3

* Mon Jan 21 2008 Marc Wiriadisastra <marc@mwiriadi.id.au> - 0.5.0-6
- Added python sitearch instead of site lib
- Removed sitelib declaration

* Sat Jan 19 2008 Marc Wiriadisastra <marc@mwiriadi.id.au> - 0.5.0-5
- Moved static object around thanks parag

* Mon Jan 14 2008 Marc Wiriadisastra <marc@mwiriadi.id.au> - 0.5.0-4
- Fixed spec sheet

* Mon Jan 14 2008 Marc Wiriadisastra <marc@mwiriadi.id.au> - 0.5.0-3
- Add devel package
- Remove static libraries

* Mon Jan 14 2008 Marc Wiriadisastra <marc@mwiriadi.id.au> - 0.5.0-2
- Changed premissions on generate.py
- Removed static package

* Sun Jan 13 2008 Marc Wiriadisastra <marc@mwiriadi.id.au> - 0.5.0-1
- initial spec file with static libraries in static file
