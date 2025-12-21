# MiniStack Why3/WhyML Spike
# Prerequisites: why3 installed with provers (alt-ergo, z3, cvc4)

.PHONY: verify ide extract clean

# Verify with default prover (Alt-Ergo)
verify:
	why3 prove MiniStack.mlw

# Verify with all available provers
verify-all:
	why3 prove -P alt-ergo -P z3 -P cvc4 MiniStack.mlw

# Open Why3 IDE for interactive proof
ide:
	why3 ide MiniStack.mlw

# Extract to OCaml
extract: verify
	mkdir -p ocaml-out
	why3 extract -D ocaml64 MiniStack.mlw -o ocaml-out/

# Build extracted OCaml (after extraction)
ocaml-build: extract
	cd ocaml-out && ocamlfind ocamlopt -package zarith -linkpkg -o ministack *.ml

# List configured provers
provers:
	why3 config list-provers

# Replay saved proofs (if session exists)
replay:
	why3 replay MiniStack.mlw

clean:
	rm -rf ocaml-out
	rm -rf MiniStack/   # Why3 session directory
