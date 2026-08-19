# StaticEng Validation

`staticeng_validate` failed on pre-existing repository-wide CodeMap debt: broken links in `.staticeng/codemap.yml` and missing source CodeMaps across hundreds of directories

`staticeng_repair` dry-run confirmed that applying repair would create hundreds of CodeMaps and normalize unrelated historical artifacts. Repair was not applied because the task explicitly limits implementation to the two diagnosed corrections and mapped existing-file tests

The validator reported no task-specific evidence or task-file defect
