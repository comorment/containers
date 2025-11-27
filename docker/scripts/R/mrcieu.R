require(devtools)
repos <- c("https://mrcieu.r-universe.dev", "https://cloud.r-project.org")

packages <- list(
  "GenomicSEM" = "0.0.5",
  "genetics.binaRies" = "0.1.2",
  "gwasglue2" = "0.0.0.9000",
  "gwasvcf" = "0.1.5",
  "MRPRESSO" = "1.0",
  "MRMix" = "0.1.0",
  "RadialMR" = "1.2.1",
  "mr.raps" = "0.4.3",
  "TwoSampleMR" = "0.6.24",
  "gwasglue" = "0.0.0.9001",
  "MRBEE" = "0.1.0",
  "MVMR" = "0.4.2")

for (package in names(packages)) {
  version <- packages[[package]]
  cat("Installing package ", package, " from MRCIEU with version ", version, "\n")
  tryCatch(
  {
    devtools::install_version(package, version=version, repos=repos)
  },
  error = function(e) {
    cat("Error occurred during package installation:\n")
    print(e)
    quit(status=1, save="no")
  },
  finally = {
  }
 )
}
