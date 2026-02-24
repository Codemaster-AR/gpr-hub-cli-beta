class GprHubBeta < Formula
  include Language::Python::Virtualenv

  desc "GPR Image Reader and AI Analyzer"
  homepage "https://github.com/Codemaster-AR/GPR-Hub-Python"
  # This URL points to a specific tag based on the local setup.py version (4.0.0)
  # and corresponds to the content of the beta branch.
  url "https://github.com/Codemaster-AR/GPR-Hub-CLI-Beta/archive/refs/tags/v6.0.0-beta.tar.gz"
  sha256 "9db928f554471c3c00fdabd0d84c571121d027863f5659939a756705779d93344"
  license "MIT"

  # Updated dependencies based on analysis of main.py and user feedback
  depends_on "python@3.12"
  depends_on "libffi" # For cryptography
  depends_on "openssl@3" # For cryptography

  def install
    # 1. Create the virtualenv
    venv = virtualenv_create(libexec, "python3.12")

    # 2. Manually install pip inside the venv just in case it's missing
    system venv.python, "-m", "ensurepip", "--upgrade"

    # Set environment variables for compilation of native extensions like cryptography
    # This ensures they link against Homebrew's openssl and libffi
    ENV.prepend_path "PATH", venv.bin
    ENV["LDFLAGS"] = "-L#{Formula["openssl@3"].opt_lib} -L#{Formula["libffi"].opt_lib}"
    ENV["CFLAGS"] = "-I#{Formula["openssl@3"].opt_include} -I#{Formula["libffi"].opt_include}"

    # 3. Use the venv's python to run pip and install your package
    # This ensures all dependencies in setup.py are handled
    system venv.python, "-m", "pip", "install", "-v", "--ignore-installed", buildpath

    # 4. Link the executable using a wrapper
    venv.install_wrapper "gpr-hub"
  end

  test do
    # Assuming --version or a similar command exists for basic functionality check
    system "#{bin}/gpr-hub", "--version"
  end
end
