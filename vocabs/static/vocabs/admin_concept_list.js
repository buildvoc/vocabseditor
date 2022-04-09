function getCheckboxFromResult(result){
    return result.children[0].children[0];
}

function getLabelFromResult(result){
    return result.children[1].children[0].innerHTML;
}

function isChecked(result){
    return getCheckboxFromResult(result).checked;
}

function check(result){
    getCheckboxFromResult(result).checked = true;
}

function addAnnifActionOption(){
    const newOption = document.createElement('option');
    newOption.value = 'annif-learn';
    newOption.textContent = 'Annif learn';
    document.querySelector('.actions select').appendChild(newOption);
}

function addLoadingBar(){
    const bar = document.createElement('div');
    const loadingBar = document.createElement('div');
    bar.classList.add('bar');
    loadingBar.classList.add('loading-bar');
    bar.appendChild(loadingBar);
    document.querySelector('body').insertAdjacentElement('afterbegin', bar);
}

function startLoading(){
    document.querySelector('.loading-bar').style = `width: 25%`;
}

function finishLoading(){
    document.querySelector('.loading-bar').style = `width: 100%`;
    setTimeout(() => document.querySelector('.loading-bar').style = `width: 0`, 800);
}

function handleAPIError(errMsg){
    document.querySelector('.error-modal').textContent = errMsg;
    document.querySelector('.error-modal').classList.add('show');
}

async function handleAnnifAPIError(response, data){
    setAnnifReponseUI(response, data);
}

function hideError(){
    document.querySelector('.error-modal').classList.remove('show');
}

async function setAnnifReponseUI(response, data){
    let headersString = '';
    for(const [headerKey, headerValue] of response.headers.entries()){
        headersString += `${headerKey}: ${headerValue}; `;
    }
    document.querySelector('#annif-response-body').value = JSON.stringify(data, null, 2);
    document.querySelector('#annif-response-headers').value = headersString;
    document.querySelector('#annif-response-status').value = response.status;
}

function scrollToForm(){
    document.querySelector('#annif-response-body').scrollIntoView({
        behavior: 'smooth',
    });
}

document.addEventListener("DOMContentLoaded", function() { 
    addAnnifActionOption();
    addLoadingBar();
    const actionsForm = document.querySelector('#changelist-form');
    actionsForm.addEventListener('submit', async function(e){
        const actionsSelect = document.querySelector('.actions select');
        if(actionsSelect.value === 'annif-learn'){
            e.preventDefault();
            const concepts = Array.from(document.querySelector('.results > #result_list > tbody').children);
            const chosenConceptLabels = concepts.filter(concept => isChecked(concept)).map(concept => getLabelFromResult(concept));
            const host = new URL(window.location.href).origin;
            startLoading();
            scrollToForm();
            try{
                hideError();
                const conceptsResponse = await fetch(`${host}/vocabs/concepts/get_from_labels?concept_labels=${JSON.stringify(chosenConceptLabels)}`);
                const conceptsData = await conceptsResponse.json();
                if(conceptsData.error !== undefined){
                    handleAPIError(conceptsData.error);
                    return;
                }
                if(conceptsData.some(concept => concept.uri === '')){
                    handleAPIError('One or more concepts have no related field.')
                    return;
                }
                else if(conceptsData.some(concept => concept.note === null)){
                    handleAPIError('One or more concepts have no concept note.')
                    return;
                }
                else{
                    const annifForm = document.querySelector('#annif-learn-form');
                    const formData = new FormData(annifForm);
                    
                    let annifAddress = formData.get('annif-url').trim();             
                    if(annifAddress.at(-1) === '/')
                        annifAddress = annifAddress.slice(0, annifAddress.length - 1);
                    const projectId = formData.get('project-id').trim();
                    if(annifAddress === ''){
                        handleAPIError('Anniff Adress is required.');
                        return;
                    }
                    if(projectId === ''){
                        handleAPIError('Project Id is required.');
                        return;
                    }
                    const annifResponse = await fetch(`${annifAddress}/projects/${projectId}/learn`, {
                        method: 'POST',
                        body: JSON.stringify(conceptsData),
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    });
                    setAnnifReponseUI(annifResponse, 'No content');
                    if(annifResponse.status === 204){
                        const markAsTrainedResponse = await fetch(`${host}/vocabs/concepts/mark_as_trained/`, {
                            method: 'POST',
                            body: JSON.stringify(chosenConceptLabels),
                        });
                        if(markAsTrainedResponse.status !== 204){
                            handleAPIError('An unexpected error happened, try again later.')
                        }
                        hideError();
                    }
                    else{
                        const annifResponseData = await annifResponse.json();
                        handleAnnifAPIError(annifResponse, annifResponseData);
                        return;
                    }
                }
            }
            catch(err){
                console.log(err);
                handleAPIError('An unexpected error happened, try again later.')
            }
            finally{
                finishLoading();
            }
        }
    });
});
