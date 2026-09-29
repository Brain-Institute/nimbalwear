from nimbalwear import Study

# creates study folder structure with template devices.csv and collections.csv files
# study = Study(r"C:/Users/kweber/Desktop/OND09/test_project", create=True)

# initiate 'study' object for pipeline run
study = Study(r"C:/Users/kweber/Desktop/OND09/test_project")
study.run_pipeline()
