%{?scl:%scl_package rubygem-%{gem_name}}
%{!?scl:%global pkg_name %{name}}

%global gem_name shoulda-context

Name: %{?scl_prefix}rubygem-%{gem_name}
Version: 1.2.1
Release: 8%{?dist}
Summary: Context framework extracted from Shoulda
Group: Development/Languages
License: MIT
URL: https://github.com/thoughtbot/shoulda-context
Source0: https://rubygems.org/gems/%{gem_name}-%{version}.gem

Requires:      %{?scl_prefix_ruby}ruby(release)
Requires:      %{?scl_prefix_ruby}ruby(rubygems)
BuildRequires: %{?scl_prefix_ruby}ruby(release)
BuildRequires: %{?scl_prefix_ruby}rubygems-devel
BuildRequires: %{?scl_prefix_ruby}ruby
BuildRequires: %{?scl_prefix_ruby}rubygem(bundler)
BuildRequires: %{?scl_prefix}rubygem(jquery-rails)
BuildRequires: %{?scl_prefix_ruby}rubygem(minitest)
BuildRequires: %{?scl_prefix}rubygem(mocha)
BuildRequires: %{?scl_prefix}rubygem(rails)
BuildRequires: %{?scl_prefix}rubygem(sass-rails)
BuildRequires: %{?scl_prefix}rubygem(sqlite3)
BuildRequires: %{?scl_prefix_ruby}rubygem(test-unit)
BuildArch:     noarch
Provides:      %{?scl_prefix}rubygem(%{gem_name}) = %{version}

# Explicitly require runtime subpackage, as long as older scl-utils do not generate it
Requires: %{?scl_prefix}runtime

%description
Shoulda's contexts make it easy to write understandable and maintainable
tests for Test::Unit. It's fully compatible with your existing tests in
Test::Unit, and requires no retooling to use.

Refer to the shoulda gem if you want to know more about using shoulda
with Rails or RSpec.

%package doc
Summary: Documentation for %{pkg_name}
Group: Documentation
Requires: %{?scl_prefix}%{pkg_name} = %{version}-%{release}
BuildArch: noarch

%description doc
Documentation for %{pkg_name}.

%prep
%{?scl:scl enable %{scl} - << \EOF}
gem unpack %{SOURCE0}
%{?scl:EOF}

%setup -q -D -T -n  %{gem_name}-%{version}

%{?scl:scl enable %{scl} - << \EOF}
gem spec %{SOURCE0} -l --ruby > %{gem_name}.gemspec
%{?scl:EOF}

# Fix wrong-file-end-of-line-encoding for rpmlint
sed -i 's/\r$//' MIT-LICENSE

# Remove /usr/bin/env from shebang so RPM doesn't consider this a dependency
%{?scl:scl enable %{scl} - << \EOF}
sed -i -e "s|^#\!/usr/bin/env ruby|#\!`which ruby`|" bin/convert_to_should_syntax
%{?scl:EOF}

# Remove zero-length developer-only file
rm test/fake_rails_root/vendor/plugins/.keep
sed -i 's|"test/fake_rails_root/vendor/plugins/.keep",||' %{gem_name}.gemspec

%build
# Create the gem as gem install only works on a gem file
%{?scl:scl enable %{scl} - << \EOF}
gem build %{gem_name}.gemspec
%gem_install
%{?scl:EOF}

%install
mkdir -p %{buildroot}%{gem_dir}
cp -pa .%{gem_dir}/* \
        %{buildroot}%{gem_dir}/

mkdir -p %{buildroot}%{_bindir}
cp -pa .%{_bindir}/* \
        %{buildroot}%{_bindir}/

find %{buildroot}%{gem_instdir}/bin -type f | xargs chmod a+x

%check
%{?scl:scl enable %{scl} - << \EOF}
set -e
pushd .%{gem_instdir}
# Remove locks to be able to use system dependencies.
rm gemfiles/*.lock

# Relax mocha and test-unit dependencies.
sed -i '/dependency.*mocha/ s/0.9.10/1.0/' shoulda-context.gemspec
sed -i '/dependency.*test-unit/ s/2.1.0/3.0/' shoulda-context.gemspec

# Get rid of unnecessary dependencies.
sed -i '/dependency.*appraisal/d' shoulda-context.gemspec
sed -i '/dependency.*rails/d' shoulda-context.gemspec
sed -i '/dependency.*rake/d' shoulda-context.gemspec

# Use RoR available in build root.
sed -i '/gem "rails"/ s/, :github=>"rails\/rails", :branch=>"4-1-stable"//' gemfiles/rails_4_1.gemfile

# Fix compatibility with Mocha 1.0+.
# https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=743071
sed -i "/require 'mocha'/ s/mocha/mocha\/setup/" test/test_helper.rb

# Fix compatibility with RoR 4.2.
sed -i "/require 'rails\/all'/ a\      ActiveSupport::TestCase.test_order = :random" \
  test/shoulda/test_framework_detection_test.rb

BUNDLE_GEMFILE=gemfiles/test_unit.gemfile bundle exec ruby -Itest -e 'Dir.glob "./test/**/*_test.rb", &method(:require)'
BUNDLE_GEMFILE=gemfiles/minitest_5_x.gemfile bundle exec ruby -Itest -e 'Dir.glob "./test/**/*_test.rb", &method(:require)'
BUNDLE_GEMFILE=gemfiles/rails_4_1.gemfile bundle exec ruby -Itest -e 'Dir.glob "./test/**/*_test.rb", &method(:require)'
popd
%{?scl:EOF}

%files
%dir %{gem_instdir}
%doc %{gem_instdir}/MIT-LICENSE
%exclude %{gem_instdir}/.*
%{_bindir}/convert_to_should_syntax
%{gem_instdir}/bin
%{gem_libdir}
%exclude %{gem_cache}
%{gem_spec}

%files doc
%doc %{gem_docdir}
%doc %{gem_instdir}/README.md
%doc %{gem_instdir}/CONTRIBUTING.md
%{gem_instdir}/Appraisals
%{gem_instdir}/Gemfile
%{gem_instdir}/gemfiles
%{gem_instdir}/init.rb
%dir %{gem_instdir}/rails
%{gem_instdir}/rails/init.rb
%{gem_instdir}/Rakefile
%{gem_instdir}/shoulda-context.gemspec
%{gem_instdir}/tasks
%{gem_instdir}/test

%changelog
* Fri Apr 08 2016 Pavel Valena <pvalena@redhat.com> - 1.2.1-8
- Fix ownership of %%{gem_instdir}/rails - rhbz#1090361

* Wed Apr 06 2016 Pavel Valena <pvalena@redhat.com> - 1.2.1-7
- Fix: build should fail on test failure

* Thu Mar 10 2016 Pavel Valena <pvalena@redhat.com> - 1.2.1-6
- Enable scl around 'Fixing the shebags'

* Thu Mar 03 2016 Pavel Valena <pvalena@redhat.com> - 1.2.1-5
- Fix shebang path to ruby

* Wed Mar 02 2016 Pavel Valena <pvalena@redhat.com> - 1.2.1-4
- Add scl macros

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Fri Jun 26 2015 Vít Ondruch <vondruch@redhat.com> - 1.2.1-2
- Fix test suite compatibility with latest Mocha and RoR.

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.2.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed Jul 02 2014 Vít Ondruch <vondruch@redhat.com> - 1.2.1-1
- Update to shoulda-context 1.2.1.

* Tue Nov 05 2013 Ken Dreyer <ktdreyer@ktdreyer.com> - 1.1.6-2
- Update to shoulda-context 1.1.6
- Clean up comments
- Remove unnecessary BR: on ruby
- Exclude developer-only files from binary packages

* Tue Aug 27 2013 Ken Dreyer <ktdreyer@ktdreyer.com> - 1.1.5-1
- Initial package
