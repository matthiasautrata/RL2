# MiniStack Dafny Spike
# Prerequisites: dafny installed (brew install dafny or similar)

.PHONY: verify run extract clean

# Verify the Dafny code (proofs and assertions)
verify:
	dafny verify MiniStack.dfy

# Run the tests (uses Dafny interpreter)
run:
	dafny run MiniStack.dfy

# Extract to Go
extract: verify
	mkdir -p go-out
	dafny build --target:go -o go-out/ministack MiniStack.dfy

# Build and run extracted Go
go-run: extract
	cd go-out && go run ministack.go

clean:
	rm -rf go-out
