package main

import (
  "os"
  "log"
  "fmt"
  "strings"
  "io/ioutil"
  "gopkg.in/yaml.v2"
)

var specfile string;

func YamlMerge(specFile string, trigFile string) {
  log.Printf("  Merging %s an %s", specFile, trigFile)

  var spec map[string]interface{}
  bs, err := ioutil.ReadFile(specFile)
  if err != nil {
      panic(err)
  }
  if err := yaml.Unmarshal(bs, &spec); err != nil {
      panic(err)
  }

  var trig map[string]interface{}
  bs, err = ioutil.ReadFile(trigFile)
  if err != nil {
      panic(err)
  }
  if err := yaml.Unmarshal(bs, &trig); err != nil {
      panic(err)
  }

  // for k, v := range trig["triggers"] {
  //     log.Printf("k: %s, v: %s", k, v)
  //     spec[k] = v
  // }

  log.Printf(spec["spec"]);
  bs, err = yaml.Marshal(spec)
  if err != nil {
      panic(err)
  }
  if err := ioutil.WriteFile(specFile, bs, 0644); err != nil {
      panic(err)
  }
}

func FileExists (filename string) bool {
  if _, err := os.Stat(filename); os.IsNotExist(err) {
    return false
  }
  return true
}

func ProcessFile(file string)  {
  if ! FileExists(file) {
    log.Printf("File %s does not exist. Ignore!", file);
    return
  }
  info, _ := os.Stat(file);
  if info.IsDir() {
    ProcessDir(file)
    return
  }
  log.Printf("Processing file %s", file);
  YamlMerge(specfile, file);
}

func ProcessDir(dir string)  {
  log.Printf("Processing folder %s", dir);
  files, err := ioutil.ReadDir(dir)
  if err != nil {
    log.Fatal(err);
    return
  }
  for _, subfile := range files {
    ProcessFile(fmt.Sprintf("%s/%s", dir, subfile.Name()))
  }
}

func main() {

  // Set properties of the predefined Logger, including
  // the log entry prefix and a flag to disable printing
  // the time, source file, and line number.
  log.SetPrefix("PTM: ")
  log.SetFlags(0)

  specfile=os.Getenv("SPEC");
  if len(specfile) == 0 {
    log.Fatal("SPEC environment variable is not defined!")
  }

  if ! FileExists(specfile) {
    log.Fatal(fmt.Sprintf("Pipeline spec file '%s' does not exist!", specfile));
  }

  var triggers=os.Getenv("TRIGGERS");
  if len(triggers) == 0 {
    log.Print("TRIGGERS environment variable is not defined!")
  } else {
    s :=strings.Split(triggers, " ");
    for _, f := range s {
      ProcessFile(f)
    }
  }

}
