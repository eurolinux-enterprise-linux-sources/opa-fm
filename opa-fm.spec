Name: opa-fm
Epoch: 1
Version: 10.9.0.0.204
Release: 1%{?dist}
Summary: Intel Omni-Path Fabric Management Software

Group: System Environment/Daemons
License: GPLv2 or BSD
Url: https://github.com/01org/opa-fm
# tarball created by:
# git clone https://github.com/01org/opa-fm.git
# cd opa-fm
# git archive --format=tar --prefix=opa-fm-%{version}/ \
# d6ef451205996ba48a72a0a68ef674e002099e53 | xz > opa-fm-%{version}.tar.xz
Source0: %{name}-%{version}.tar.xz
Source2:	opa-fm.ini

# bz1262327 needs Patch0002
Patch0002: 0001-Fix-well-known-tempfile-issue-in-script.patch
Patch3:	opa-fm_add_dist_to_list.patch

BuildRequires: openssl-devel, expat-devel, python, gcc
BuildRequires: libibverbs-devel >= 1.2.0
BuildRequires: libibumad-devel
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
%setup -q
%patch0002 -p1
%patch3 -p1

# Make it possible to override hardcoded compiler flags
sed -i -r -e 's/(release_C(C)?OPT_Flags\s*)=/\1?=/' Makerules/Target.LINUX.GNU.*

%build
export CFLAGS='%{optflags}'
export CXXFLAGS='%{optflags}'
export release_COPT_Flags='%{optflags}'
export release_CCOPT_Flags='%{optflags}'
cd Esm
./fmbuild

%install
BUILDDIR=%{_builddir} DESTDIR=%{buildroot} LIBDIR=%{_libdir} RPM_INS=n ./Esm/fm_install.sh
chmod 644 %{buildroot}/%{_unitdir}/opafm.service
mkdir -p %{buildroot}/%{_localstatedir}/usr/lib/opa-fm/
chmod a-x %{buildroot}/%{_prefix}/share/opa-fm/opafm_src.xml

%post
%systemd_post opafm.service

%preun
%systemd_preun opafm.service

%postun
%systemd_postun_with_restart opafm.service

%files
%doc Esm/README
%{_unitdir}/opafm.service
%config(noreplace) %{_sysconfdir}/opa-fm/opafm.xml
%config(noreplace) %{_sysconfdir}/opa-fm/opafm_pp.xml
%{_sysconfdir}/opa-fm/vfs
%{_sysconfdir}/opa-fm/dgs
%{_prefix}/lib/opa-fm/bin/*
%{_prefix}/lib/opa-fm/runtime/*
%{_prefix}/share/opa-fm/*
%{_sbindir}/opafmcmd
%{_sbindir}/opafmcmdall
%{_sbindir}/opafmconfigpp
%{_mandir}/man8/*


%changelog
* Thu Aug 08 2019 Scientific Linux Auto Patch Process <SCIENTIFIC-LINUX-DEVEL@LISTSERV.FNAL.GOV>
- Added Patch: opa-fm_add_dist_to_list.patch
-->  Detect SL is an EL
- Added Source: opa-fm.ini
-->  Config file for automated patch script

* Wed Jan 30 2019 Honggang Li <honli@redhat.com> - 10.9.0.0.204-1
- Rebase to upstream release 10.9.0.0.204
- Resolves: bz1637241

* Thu Apr 19 2018 Honggang Li <honli@redhat.com> - 10.7.0.0.141-1
- Rebase to upstream release 10.7.0.0.141
- Resolves: bz1483559

* Thu Oct 19 2017 Honggang Li <honli@redhat.com> - 10.5.1.0.1-1
- Rebase to upstream release 10.5.1.0.1
- Resolves: bz1452787, bz1500903

* Fri Mar 17 2017 Honggang Li <honli@redhat.com> - 10.3.1.0-8
- Rebase to upstream branch v10_3_1 as required.
- Clean up change log.
- Apply Epoch tag.
- Resolves: bz1257452, bz1382792

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
