name := "ministack-stainless"
version := "0.1.0"
scalaVersion := "3.3.1"

// Stainless requires specific Scala version
// See https://epfl-lara.github.io/stainless/installation.html

libraryDependencies += "ch.epfl.lara" %% "stainless-library" % "0.9.8"

// For running without verification (after verification passes)
Compile / run / mainClass := Some("MiniStack")
