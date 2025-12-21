# MiniStack Stainless Spike
# Prerequisites: stainless installed (https://epfl-lara.github.io/stainless/)

.PHONY: verify run clean

# Verify the Stainless code
# Stainless is run as a standalone tool
verify:
	stainless MiniStack.scala

# Verify with more verbose output
verify-verbose:
	stainless --debug=verification MiniStack.scala

# After verification, can compile and run with scalac
# Note: Stainless library provides the stainless.* imports
run: verify
	@echo "Stainless code is verified. For runtime, compile with scalac."
	@echo "Stainless-verified code runs natively on JVM - no extraction step."

clean:
	rm -rf .stainless-cache
	rm -rf target
