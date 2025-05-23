terraform { 
  cloud { 
    organization = "globalhealthdatascience" 

    workspaces { 
      name = "globalhealthworkspace" 
    } 
  } 
}