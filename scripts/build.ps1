param(
    [ValidateSet("gom", "campus")]
    [string]$Backend = "gom",
    [switch]$Force
)

$argsList = @("build", "--backend", $Backend)
if ($Force) { $argsList += "--force" }
kaa-data @argsList