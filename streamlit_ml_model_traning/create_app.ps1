az group create --name streamlit_ml_grs_fit --location westus2 ;
az acr create --name streamlitmlgrsfit --resource-group streamlit_ml_grs_fit --sku Basic --admin-enabled true ;
az acr credential show --resource-group streamlit_ml_grs_fit --name streamlitmlgrsfit ;
docker login streamlitmlgrsfit.azurecr.io  ;
docker tag streamlit_ml_grs_fit streamlitmlgrsfit.azurecr.io/streamlit_ml_grs_fit:latest ;
docker push streamlitmlgrsfit.azurecr.io/streamlit_ml_grs_fit:latest ;

az containerapp env create --name streamlit-ml-grs-fit-env --resource-group streamlit_ml_grs_fit --location westus2 ;
az containerapp create `
    --name grs-ml `
    --resource-group streamlit_ml_grs_fit `
    --environment streamlit-ml-grs-fit-env `
    --image streamlitmlgrsfit.azurecr.io/streamlit_ml_grs_fit:latest `
    --target-port 8501 `
    --ingress 'external' `
    --registry-server streamlitmlgrsfit.azurecr.io ;