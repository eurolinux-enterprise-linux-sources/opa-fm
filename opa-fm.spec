%global Intel_Release 145

Name: opa-fm
Version: 10.1.0.0
Release: %{Intel_Release}%{?dist}
Summary: Intel Omni-Path Fabric Management Software

Group: System Environment/Daemons
License: BSD
Url: https://github.com/01org/opa-fm
# tarball created by:
# git clone https://github.com/01org/opa-fm.git
# cd opa-fm
# git archive --format=tar --prefix=opa-fm-%{version}-%{Intel_Release}/ \
# 78e4916cc1928689d74f5da9c3047c6cafe24218 | xz > opa-fm-%{version}-%{Intel_Release}.tar.xz
Source0: %{name}-%{version}-%{Intel_Release}.tar.xz

Patch0001: 0001-opafmd-larger-array-to-hold-program-path.patch
# bz1262327 needs Patch0002
Patch0002: 0001-Fix-well-known-tempfile-issue-in-script.patch

BuildRequires: autoconf
BuildRequires: systemd
BuildRequires: zlib-devel, openssl-devel, expat-devel
BuildRequires: libibmad-devel, libibverbs-devel >= 1.2.0
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
Requires: libhfi1
ExclusiveArch: x86_64

%description
opa-fm contains Intel Omni-Path fabric management applications. This
includes: the Subnet Manager, Baseboard Manager, Performance Manager,
Fabric Executive, and some fabric management tools.

%prep
%setup -q -n %{name}-%{version}-%{Intel_Release}
%patch0001 -p1
%patch0002 -p1

# Make it possible to override hardcoded compiler flags
sed -i -r -e 's/(release_C(C)?OPT_Flags\s*)=/\1?=/' Makerules/Target.LINUX.GNU.*

# A crude hack from necessity. Upstream hardcodes "/opt/opafm" in many places.
# Packaging guidelines disallow installation into /opt.
# Instead we'll use /usr/lib/opa-fm/ (NOT _libdir !) as this package's private
# directory.
sed -i -e 's#/opt/opafm#/usr/lib/opa-fm#g' $(grep -r -l '/opt/opafm' .)
# The same holds for opa-ff, which this package references:
sed -i -e 's#/opt/opa#/usr/lib/opa-ff#g'   $(grep -r -l '/opt/opa' .)

%build
export CFLAGS='%{optflags}'
export CXXFLAGS='%{optflags}'
export release_COPT_Flags='%{optflags}'
export release_CCOPT_Flags='%{optflags}'
cd Esm
./fmbuild -V %{version}.%{release}

%install
%global fm_mans opafmcmd.8 opafmcmdall.8

install -D -m 644 stage.rpm/opafm.service %{buildroot}/%{_unitdir}/opafm.service
install -D -m 755 stage.rpm/opafmctrl %{buildroot}/usr/lib/opa-fm/bin/opafmctrl
install -D -m 755 stage.rpm/opafmd %{buildroot}/usr/lib/opa-fm/bin/opafmd

install -D -m 644 stage.rpm/opafm.xml %{buildroot}%{_sysconfdir}/sysconfig/opafm.xml
install -D -m 755 stage.rpm/opafm.info %{buildroot}%{_sysconfdir}/sysconfig/opa/opafm.info

install -D stage.rpm/fm_capture %{buildroot}/usr/lib/opa-fm/bin/fm_capture
install -D stage.rpm/fm_cmd %{buildroot}/usr/lib/opa-fm/bin/fm_cmd
install -D stage.rpm/fm_cmdall %{buildroot}/usr/lib/opa-fm/bin/fm_cmdall
install -D stage.rpm/smpoolsize %{buildroot}/usr/lib/opa-fm/bin/smpoolsize

install -D stage.rpm/sm %{buildroot}/usr/lib/opa-fm/runtime/sm
install -D stage.rpm/fe %{buildroot}/usr/lib/opa-fm/runtime/fe

install -D stage.rpm/config_check %{buildroot}/usr/lib/opa-fm/etc/config_check
install -D stage.rpm/config_convert %{buildroot}/usr/lib/opa-fm/etc/config_convert
install -D stage.rpm/config_diff %{buildroot}/usr/lib/opa-fm/etc/config_diff
install -D stage.rpm/config_generate %{buildroot}/usr/lib/opa-fm/etc/config_generate
install -D stage.rpm/opafm %{buildroot}/usr/lib/opa-fm/etc/opafm
install -D stage.rpm/opafm.arch %{buildroot}/usr/lib/opa-fm/etc/opafm.arch
install -D stage.rpm/opafm.info %{buildroot}/usr/lib/opa-fm/etc/opafm.info
install -D Esm/ib/src/linux/startup/opafm_src.xml %{buildroot}/usr/lib/opa-fm/etc/opafm_src.xml

install -D stage.rpm/opafm.xml %{buildroot}/usr/lib/opa-fm/etc/opafm.xml
install -D stage.rpm/opaxmlextract %{buildroot}/usr/lib/opa-fm/etc/opaxmlextract
install -D stage.rpm/opaxmlfilter %{buildroot}/usr/lib/opa-fm/etc/opaxmlfilter

mkdir -p %{buildroot}%{_sbindir}
mkdir -p %{buildroot}%{_mandir}/man8
ln -s /usr/lib/opa-fm/bin/fm_cmd %{buildroot}%{_sbindir}/opafmcmd
ln -s /usr/lib/opa-fm/bin/fm_cmdall %{buildroot}%{_sbindir}/opafmcmdall
mkdir -p %{buildroot}/%{_localstatedir}/usr/lib/opa-fm/

cd stage.rpm
cp -t %{buildroot}%{_mandir}/man8 %fm_mans

%post
%systemd_post opafm.service

%preun
%systemd_preun opafm.service

%postun
%systemd_postun_with_restart opafm.service

%files
%doc Esm/README
%{_unitdir}/opafm.service
%config(noreplace) %{_sysconfdir}/sysconfig/opafm.xml
%{_sysconfdir}/sysconfig/opa/opafm.info
%{_prefix}/lib/opa-fm/bin/*
%{_prefix}/lib/opa-fm/etc/*
%{_prefix}/lib/opa-fm/runtime/*
%{_sbindir}/opafmcmd
%{_sbindir}/opafmcmdall
%{_localstatedir}/usr/lib/opa-fm/
%{_mandir}/man8/*


%changelog
* Sun Jul 10 2016 Honggang Li <honli@redhat.com> - 10.1.0.0-145
- Rebase to latest upstream release.
- Related: bz1273151

* Tue Jun 21 2016 Honggang Li <honli@redhat.com> - 10.0.1.0-4
- Create private state dir.
- Resolves: bz1348477

* Thu Jun  2 2016 Honggang Li <honli@redhat.com> - 10.0.1.0-3
- Requires libhfi1.
- Remove executable permission bit of opafm.service.
- Resolves: bz1341971

* Thu May 26 2016 Honggang Li <honli@redhat.com> - 10.0.1.0-2
- Rebase to upstream release 10.0.1.0.
- Related: bz1273151

* Mon Sep 28 2015 Honggang Li <honli@redhat.com> - 10.0.0.0-444
- Update the N-V-R
- Related: bz1262327

* Mon Sep 28 2015 Honggang Li <honli@redhat.com> - 10.0.0.0-443
- Apply one missed patch to fix various /tmp races
- Revert the script for building (S)RPMs
- Resolves: bz1262327

* Thu Sep 24 2015 Honggang Li <honli@redhat.com> - 10.0.0.0-442
- Fix typo in changelog
- Related: bz1262327

* Wed Sep 23 2015 Honggang Li <honli@redhat.com> - 10.0.0.0-441
- Fix various /tmp races
- Resolves: bz1262327

* Wed Aug 26 2015 Michal Schmidt <mschmidt@redhat.com> - 10.0.0.0-440
- Respect optflags.
- Avoid overflowing prog path due to /opt -> /usr/lib substitution.
- Resolves: bz1257087
- Resolves: bz1257093

* Mon Aug 24 2015 Michal Schmidt <mschmidt@redhat.com> - 10.0.0.0-439
- Update to new upstream snapshot with unbundled expat.
- Related: bz1173302

* Tue Aug 18 2015 Michal Schmidt <mschmidt@redhat.com> - 10.0.0.0-438
- Initial packaging for RHEL, based on upstream spec file.
- Cleaned up spec.
- Moved /opt/opafm -> /usr/lib/opa-fm.
- Fix scriptlets.

* Thu Oct 09 2014 Kaike Wan <kaike.wan@intel.com> - 10.0.0.0-177
- Initial version
