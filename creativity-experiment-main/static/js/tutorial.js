// Copyright (C) 2022  TranslateGreat LLC.  All rights reserved.
"use strict";


/*
--TABLE OF CONTENTS--

Initialization:
    - call tutorial(settings) to generate tutorial instance
    - initialization does not auto-start tutorial

tutorial.start:
    - function to start tutorial
    - next(), previous(), and set() can be called prior to calling start()
    - tutorial will begin at index of tutorial.tutorialIndex
    - tutorialIndex == 0 if other function hadn't been called before (such as next())

tutorial.next: 
    - function 

tutorial.previous:

tutorial.set:

tutorial.spotlightNextTarget:

tutorial.recalculatePositions:


--EXAMPLE CALL STACKS--

NEED TO UPDATE CALL-STACK EXMAPLES

1.
    start()
        spotlightNextTarget()
            recalculatePositions()

2.
    previous()
        spotlightNextTarget()
            recalculatePositions()  
    next()
        spotlightNextTarget()
            recalculatePositions()  
*/
  



// document.addEventListener('DOMContentLoaded', () => {
//     let allTutorialsData = JSON.parse(window.localStorage.getItem('spotlight-data'));

//     const tutorialNames = allTutorialsData.keys;
//     for (let i=0; i<tutorialNames.length; i++) {

//     }
// })




/**
 * Generate a Tutorial instance.
 * 
 * @param tutorialObject User-specified object that is used to initialize new Tutorial.
 * @returns The instance of the newly-generated Tutorial object.
 */
function tutorial(tutorialObject) {
    const tutorial = {};

    // tutorial attributes/settings
    tutorial.isActive = false;
    tutorial.steps = tutorialObject.steps;
    tutorial.stepStack = []; // step stack so we can know the exact path a user is on
    tutorial.stepHistoryStack = [];
    tutorial.settings = tutorialObject.settings;
    tutorial.tutorialLength = tutorialObject.steps.length;
    tutorial.tutorialIndex = -1; // -1 before tutorial starts
    tutorial.screenWidth = window.screen.width;
    tutorial.screenHeight = window.screen.height;
    tutorial.showChecklist = tutorialObject.settings.showChecklist;
    tutorial.mutationObserver;
    tutorial.currentSpotlightTarget = {};
    tutorial.currentURL;

    // branching attributes
    tutorial.currentlyInBranch = false;
    tutorial.branch = {};
    tutorial.branchIndex = 0;


    /**
     * Sets up tutorial for when it gets started
     * 
     * Creates all necessary HTML, adds classes and ids, loads data from localStorage, etc.
     */
    tutorial.setup = function() {
        // veil divs
        tutorial.topVeil = document.createElement('div');
        tutorial.bottomVeil = document.createElement('div');
        tutorial.leftVeil = document.createElement('div');
        tutorial.rightVeil = document.createElement('div');
        tutorial.topVeil.classList += 'tutorial-veil';
        tutorial.bottomVeil.classList += 'tutorial-veil';
        tutorial.leftVeil.classList += 'tutorial-veil';
        tutorial.rightVeil.classList += 'tutorial-veil';

        // spotlight div
        tutorial.spotlightDiv = document.createElement('div');
        tutorial.spotlightDiv.id = 'tutorial-spotlight';

        // // checklist div
        // tutorial.checkListDiv = document.createElement('div');
        // tutorial.checkListDiv.id = 'tutorial-checklist-container';

        // // checklist div event listeners
        // tutorial.checkListDiv.addEventListener('mousedown', function(e) {
        //     tutorial.checkListDiv.style.cursor = 'all-scroll';
        //     let startX = e.clientX;
        //     let startY = e.clientY;
        //     let startBcr = tutorial.checkListDiv.getBoundingClientRect();
        //     document.body.onmousemove = function(e) {
        //         let deltaX = e.clientX - startX;
        //         let deltaY = e.clientY - startY;                                                              
        //         //update position (drag)
        //         $(tutorial.checkListDiv).css("left", `${startBcr.x + deltaX}px`); 
        //         $(tutorial.checkListDiv).css("top", `${startBcr.y + deltaY}px`);
        //     }
        // });

        // tutorial.checkListDiv.addEventListener('mouseup', function() {
        //     tutorial.checkListDiv.style.cursor = 'all-scroll';
        //     document.body.onmousemove = null;
        // });

        // // checklist items container div
        // tutorial.checklistItemsContainer = document.createElement('div');
        // tutorial.checklistItemsContainer.id = 'checklist-items-container';
        // tutorial.checkListDiv.innerHTML += 
        //     `<div id="tutorial-checklist-title-container">
        //         <div id="tutorial-checklist-title">${tutorial.settings.checklistTitle}</div>
        //         <div id="tutorial-checklist-collapse" class="open"></div>
        //     </div>
        //     <div id="checklist-progress-bar-container">
        //             <div id="checklist-progress-bar"></div>
        //     </div>`;

        // exit button
        tutorial.exitBtn = document.createElement('div');
        tutorial.exitBtn.innerText = "X";
        tutorial.exitBtn.classList.add("exit-tutorial-btn");

        tutorial.exitBtn.addEventListener('click', () => {
            tutorial.finish()
        });

        tutorial.tooltipContainerDiv = document.createElement('div');
        tutorial.tooltipContainerDiv.id = 'spotlight-tooltip-all-content-container';

        tutorial.tooltipContentDiv = document.createElement('div');
        tutorial.tooltipContentDiv.id = 'spotlight-tooltip-dynamic-content-container';

        tutorial.tooltipBtnContainerDiv = document.createElement('div');
        tutorial.tooltipBtnContainerDiv.id = 'spotlight-tooltip-btn-container';

        tutorial.tooltipPrevBtn = document.createElement('button');
        tutorial.tooltipPrevBtn.innerHTML = "Previous";
        tutorial.tooltipPrevBtn.id = 'spotlight-tooltip-btn-previous';
        tutorial.tooltipPrevBtn.classList.add('spotlight-tooltip-nav-btn');

        tutorial.tooltipNextBtn = document.createElement('button');
        tutorial.tooltipNextBtn.innerHTML = "Next";
        tutorial.tooltipNextBtn.id = 'spotlight-tooltip-btn-next';
        tutorial.tooltipNextBtn.classList.add('spotlight-tooltip-nav-btn');

        tutorial.tooltipFinishBtn = document.createElement('button');
        tutorial.tooltipFinishBtn.innerHTML = "Finish";
        tutorial.tooltipFinishBtn.id = 'spotlight-tooltip-btn-finish';
        tutorial.tooltipFinishBtn.classList.add('spotlight-tooltip-nav-btn');

        tutorial.tooltipBtnContainerDiv.appendChild(tutorial.tooltipPrevBtn);
        tutorial.tooltipBtnContainerDiv.appendChild(tutorial.tooltipNextBtn);
        tutorial.tooltipBtnContainerDiv.appendChild(tutorial.tooltipFinishBtn);

        tutorial.tooltipContainerDiv.appendChild(tutorial.exitBtn);
        tutorial.tooltipContainerDiv.appendChild(tutorial.tooltipContentDiv);
        tutorial.tooltipContainerDiv.appendChild(tutorial.tooltipBtnContainerDiv);

        tutorial.tooltipNextBtn.addEventListener('click', tutorial.nextEventListener);
        tutorial.tooltipPrevBtn.addEventListener('click', tutorial.previousEventListener);
        tutorial.tooltipFinishBtn.addEventListener('click', tutorial.finish);

        // initialize tooltips
        tutorial.tippyInstance = tippy(tutorial.spotlightDiv, {
            zIndex: 2147483647,
            content: 'sample tutorial content',
            hideOnClick: false,
            arrow: true,
            allowHTML: true,
            interactive: true,
            flip: true,
            flipOnUpdate: true,
            theme: "light",
            placement: 'auto',
        });
        // hide and disable tooltip for now
        tutorial.tippyInstance.hide();
        tutorial.tippyInstance.disable();  


        // center tutorial window
        tutorial.centerDialogExitBtn = tutorial.exitBtn.cloneNode(true);

        tutorial.centerDialogExitBtn.addEventListener('click', () => {
            tutorial.finish()
        });

        tutorial.centerDialogDiv = document.createElement('div');
        tutorial.centerDialogDiv.id = 'tutorial-modal-div';
        tutorial.centerDialogTextContainer = document.createElement('div');
        tutorial.centerDialogTextContainer.style.textAlign = 'center';
        tutorial.centerDialogDiv.appendChild(tutorial.centerDialogExitBtn);
        tutorial.centerDialogDiv.appendChild(tutorial.centerDialogTextContainer);
        tutorial.centerDialogDiv.appendChild(tutorial.tooltipBtnContainerDiv);

        // Generate spotlight IDs.
        // If this tutorial's state is saved in localStorage,
        // these IDs are supposed to ALWAYS match the ones in localStorage.
        tutorial.generateStepIds(tutorial.steps);

        // Set up spotlight stack.
        for (let i=tutorial.steps.length - 1; i>=0; i--) {
            tutorial.stepStack.push(tutorial.steps[i]);
        }

        // Check if localStorage has data for this tutorial
        // If it does, use it. Otherwise, set data to default data.
        let existingData = JSON.parse(window.localStorage.getItem('spotlight-data'));

        if (!existingData || !existingData[tutorial.settings.tutorialName]) {

            existingData = (existingData)? existingData : {};
            existingData[tutorial.settings.tutorialName] = {
                "stepStack": tutorial.stepStack,
                "stepHistoryStack": tutorial.stepHistoryStack,   
                "isActive": true,
            }
            window.localStorage.setItem('spotlight-data', JSON.stringify(existingData));
        }
        else {
            // If data for this tutorial already exists in localStorage, we have 
            // to reconstruct stacks based on data saved in localStorage.
            // The reason we have to reconstruct the stacks instead of simply using the
            // ones stored in localStorage is because we are not able to save the
            // onSpotlightStart and onSpotlightEnd functions in the localStorage stacks.
            const localStorageStepHistoryStack = existingData[tutorial.settings.tutorialName].stepHistoryStack;
            tutorial.reconstructStacksFromLocalStorage(localStorageStepHistoryStack);
        }   
    }


    /**
     *    Start Method:
     *    - Initializes necessay values to begin tutorial
     *    - Adds html elements to DOM
    */
    tutorial.start = function(forceStart) {  

        const existingData = JSON.parse(window.localStorage.getItem('spotlight-data'));

        // Check localStorage to see if tutorial has been marked as finished.
        // If finished, return and do not run tutorial unless forceStart == true.
        if (!existingData[tutorial.settings.tutorialName].isActive && !forceStart) {
            return;
        }

        /*
        let checklistIndex = 0;
        for (let i=0; i<tutorial.steps.length; i++) {
            if (tutorial.steps[i].checklistText) {
                // set checklist item ids for later identification
                tutorial.steps[i].checklistId = `tutorial-checklist-item-${checklistIndex}`;
                tutorial.steps[i].checklistCheckmarkId = `tutorial-checklist-checkbox-${checklistIndex}`;
                let checklistItem = document.createElement('div');
                checklistItem.id = `tutorial-checklist-item-${checklistIndex}`;
                checklistItem.classList.add('spotlight-checklist-tutrial-item');
        
                // load checklist item into checklist div
                checklistItem.innerHTML += 
                    `<div class="svg-checkmark-wrapper">
                        <svg class="svg-checkmark" width="20" height="20" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <g id="translation-approved-check">
                                <rect id="tutorial-checklist-checkbox-${checklistIndex}" width="16" height="16" rx="2" fill="none"></rect>
                                <path id="checkmark" d="M2.46155 8.13054L6.5591 11.9332C6.77542 12.1339 7.11763 12.1046 7.29668 11.8701L13.5385 3.69231" stroke="#ffffff" stroke-width="1.5"></path>
                            </g>
                        </svg>
                    </div>
                    <div class="checklist-item-text">${tutorial.steps[i].checklistText}</div>`;
        
                tutorial.checklistItemsContainer.appendChild(checklistItem);
                tutorial.checkListDiv.appendChild(tutorial.checklistItemsContainer);
                checklistIndex++;
            }
        }
        */

        // display veil and spotlight divs
        document.body.appendChild(tutorial.spotlightDiv);
        //document.body.appendChild(tutorial.checkListDiv);
        document.body.appendChild(tutorial.topVeil);
        document.body.appendChild(tutorial.bottomVeil);
        document.body.appendChild(tutorial.leftVeil);
        document.body.appendChild(tutorial.rightVeil);

        //document.body.appendChild(tutorial.exitBtn);
        document.body.appendChild(tutorial.centerDialogDiv);

        for (let i=0; i<document.querySelectorAll('.tutorial-veil').length; i++) {       
            let veilDiv = document.querySelectorAll('.tutorial-veil')[i]
            //veilDiv.addEventListener('click', tutorial.onClick);
        }

        // when window gets resized or scrolled, recalculate position and size of spotlight
        window.addEventListener('resize', () => tutorial.recalculatePositions(true));
        document.addEventListener('scroll', () => tutorial.recalculatePositions(true));

        // if esc. key is pressed, exit tutorial
        document.addEventListener('keyup', function(e) {
            e.preventDefault();
            if (e.key == 'Escape') tutorial.close();
        });

        // DOM mutation observer so detect any changes in the page and adjust the spotlight postition/size
        tutorial.mutationObserver = new MutationObserver(tutorial.recalculatePositions);
        var config = { attributes: true, childList: true, subtree: true };
        tutorial.mutationObserver.observe(document.body, config);

        /* Setup up checklist-related items */

        // checklist dropdown btn event listener
        // document.getElementById('tutorial-checklist-collapse').addEventListener('mouseup', function() {
        //     for (let i=0; i<tutorial.classList.length; i++) {
        //         if (tutorial.classList[i] == "open") tutorial.classList.remove("open");
        //         else continue;
        //         tutorial.checklistItemsContainer.style.maxHeight = '0px';
        //         return;
        //     }
        //     tutorial.classList.add("open");
        //     tutorial.checklistItemsContainer.style.maxHeight = '250px';
        // });

        //tutorial.updateChecklistProgressBar();

        // if setting tutorial index, need to mark previous checklist items as completed
        for (let i=0; i<tutorial.tutorialIndex; i++) {
            let targetObject = tutorial.steps[i];
            // if previous spotlight was a checklist item, update checklist (cross-off that item)
            if (targetObject.checklistText) {
                let scrollTop = tutorial.checklistItemsContainer.scrollTop;
                let elemOffsetTop = $(`#${targetObject.checklistId}`)[0].offsetTop;
                if ((elemOffsetTop - scrollTop) > 240) {
                    tutorial.checklistItemsContainer.scroll({
                        left: 0, 
                        top: elemOffsetTop - 110, 
                        behavior: 'smooth'
                    });
                }
                $(`#${targetObject.checklistCheckmarkId}`)[0].setAttribute('fill', '#68cc74');
            }
        }

        tutorial.isActive = true;
        tutorial.next();
    }


    /**
     * Go to next tutorial spotlight.
     * Update localStorage.
     */
    tutorial.next = function() {
        // update tutorial index value and get next target
        if (!tutorial.currentlyInBranch) tutorial.tutorialIndex++;
        else tutorial.branchIndex++;

        let nextStep = tutorial.stepStack.pop();
        

        switch(nextStep.type) {
            // Step type: Fork
            case "fork":
                for (let i=0; i<nextStep.branches.length; i++) {
                    if (nextStep.branches[i].branchCondition()) {
                        for (let j=nextStep.branches[i].steps.length - 1; j>=0; j--) {
                            tutorial.stepStack.push(nextStep.branches[i].steps[j]);
                        }
                        tutorial.next();
                        return;
                    }
                }
                break;

            // Step type: Tutorial
            case "tutorial":
                // const tutorialObject = __USER_TUTORIALS__[nextStep.tutorialName];
                // if (tutorialObject) {
                //     for (let i=tutorialObject[nextStep].steps.length - 1; i>=0; i--) {
                //         tutorial.stepStack.push(tutorialObject[nextStep].steps[i]);
                //     }
                //     tutorial.next();
                //     return;   
                // }
                break;
       

            // Step type: Spotlight (default)
            default:                
                tutorial.currentSpotlightTarget = nextStep;
        }

        tutorial.setLocalStorage({ isActive: true });

        // if tutorial is active, continue with pre-spotlight processing
        if (tutorial.isActive) {
            // TODO: Implement logic for processing the last step of a tutorial
            tutorial.preSpotlightProcessing(true);
        }
    }


    /**
     * Go to previous tutorial spotlight
     * Update localStorage.
     */ 
    tutorial.previous = function() {
        // if tutorial is active, post-process last step
        if (tutorial.isActive) {
            // hide and disable previous tooltip
            tutorial.tippyInstance.enable(); // need to enable in order to hide
            tutorial.tippyInstance.hide();
            tutorial.tippyInstance.disable();
        }

        tutorial.currentSpotlightTarget = tutorial.stepHistoryStack.pop();

        tutorial.setLocalStorage({ isActive: true });

        // if tutorial is active, update checklist and spotlight next element
        if (tutorial.isActive) {
            //tutorial.updateChecklistProgressBar();
            tutorial.preSpotlightProcessing();
        }
    }


    /**
     * Set tutorial by passing an index value
     * 
     * !! CURRENTLY DEPRECATED !!
     * 
     * @param index Desired tutorial index to jump to.
     */
    tutorial.set = function(index) {
        if (index < 0 || index > (tutorial.tutorialLength - 1)){
            console.warn("Invalid tutorial index value. You need to pass a value between 0 and tutorialLength - 1");
            return;
        }

        tutorial.tutorialIndex = index; // update tutorial index

        if (tutorial.isActive) {
            // hide and disable previous tooltip
            tutorial.tippyInstance.enable();
            tutorial.tippyInstance.hide();
            tutorial.tippyInstance.disable();
    
            tutorial.spotlightNextTarget();
        }
    }


    /**
     * Prepares the spotlight prev/next buttons.
     * Also where user added onSpotlightStart code runs.  
     */ 
    tutorial.preSpotlightProcessing = function(spotlightObject) {
        const targetObject = tutorial.currentSpotlightTarget;
        // if defined, run onSpotlightStart function
        if (tutorial.isActive) {
            if (targetObject.onSpotlightStart) {
                targetObject.onSpotlightStart();
            }
            if (targetObject.customEventTarget) {
                const customEventTargetElement = document.querySelector(targetObject.customEventTarget);           
                customEventTargetElement.addEventListener(targetObject.customEventType, tutorial.nextEventListener); 
            }
        }

        // Check if this is the last step in the tutorial.
        // If it is, display "Finish" instead of "Next".
        if (tutorial.stepStack.length === 0) {
            tutorial.tooltipFinishBtn.style.display = 'block';
            tutorial.tooltipNextBtn.style.display = 'none';
        }
        else {
            tutorial.tooltipFinishBtn.style.display = 'none';
            tutorial.tooltipNextBtn.style.display = 'block';
        }

        // Check if user has specified that they would like to deactive the "Next" button.
        if (targetObject.deactivateNextBtn) {
            tutorial.tooltipNextBtn.disabled = true;
            tutorial.tooltipNextBtn.style.backgroundColor = 'rgb(248 247 247)';
            tutorial.tooltipNextBtn.style.cursor = 'not-allowed';
        } else {
            tutorial.tooltipNextBtn.disabled = false;
            tutorial.tooltipNextBtn.style.backgroundColor = '#dadada';
            tutorial.tooltipNextBtn.style.cursor = 'pointer';
        }
        // Check if user has specified that they would like to deactive the "Previous" button.
        if (targetObject.deactivatePrevBtn) {
            tutorial.tooltipPrevBtn.disabled = true;
            tutorial.tooltipPrevBtn.style.backgroundColor = 'rgb(248 247 247)';
            tutorial.tooltipPrevBtn.style.cursor = 'not-allowed';
        } else {
            tutorial.tooltipPrevBtn.disabled = false;
            tutorial.tooltipPrevBtn.style.backgroundColor = '#dadada';
            tutorial.tooltipPrevBtn.style.cursor = 'pointer';
        }

        // spotlight next element
        if (tutorial.isActive) tutorial.spotlightNextTarget();
    }


    /**
     * Spotlight provided target.
     * 
     * @param targetSpotlightObject Optional. Spotlight object that specifies what content to spotlight on page.
     */
    tutorial.spotlightNextTarget = function(targetSpotlightObject) {
        const targetObject = targetSpotlightObject || tutorial.currentSpotlightTarget;

        let element;
        if (targetObject.selector != 'none') { // spotlight the user-provided elem
            element = $(targetObject.selector)[0]; // always takes first element found by selector
            tutorial.centerDialogDiv.style.display = 'none';
            tutorial.tooltipContainerDiv.appendChild(tutorial.tooltipBtnContainerDiv);
            tutorial.tooltipContentDiv.innerHTML = targetObject.content;  

            // display tooltip
            setTimeout(function() {
                tutorial.tippyInstance.enable();
                tutorial.tippyInstance.setContent(tutorial.tooltipContainerDiv);
                tutorial.tippyInstance.show();
                //tutorial.tippyInstance.disable();
            }, 500);

        } else { // spotlight the native center-tutorial elem
            tutorial.centerDialogDiv.appendChild(tutorial.tooltipBtnContainerDiv);
            element = tutorial.centerDialogTextContainer;
            tutorial.centerDialogTextContainer.innerHTML = targetObject.content;
            tutorial.centerDialogDiv.style.display = 'flex';
        }

        if (tutorial.isActive) {
            // get spotlighted element and scroll into view
            element.scrollIntoView({behavior: "smooth", block: "center", inline: "center"});
            // recalculate positions of spotlight and veil divs
            tutorial.recalculatePositions();
            document.cookie = `${tutorial.settings.tutorialName}-tutorial-index=${tutorial.tutorialIndex}`;
        }
    }


    /**
     * Recalculate and update positions of spotlight and veil divs.
     * i.e. where the magic happens ;)
     * 
     * @param useInstantTransition 
     *          Specifies whether Spotlight should instantly (without transition) spotlight next content.
     */
    tutorial.recalculatePositions = function(useInstantTransition) {
        // get currently spotlighted element
        const targetObject = tutorial.currentSpotlightTarget;

        const element = (targetObject.selector != 'none')? $(targetObject.selector)[0] : tutorial.centerDialogDiv; // always takes first element found by selector
        let elemOffset = (targetObject.selector != 'none')? $(targetObject.selector).offset() : $('#tutorial-modal-div').offset();
        let elemBCR = element.getBoundingClientRect();

        let shiftX = -15;
        let shiftY = -15;
        let widthAdjust = 30;
        let heightAdjust = 30;
        
        if (targetObject.spotlightAdjustment) {
            let adjustmentObject = targetObject.spotlightAdjustment;
            if (adjustmentObject.left || adjustmentObject.left === 0) shiftX =  targetObject.spotlightAdjustment.left;
            if (adjustmentObject.top || adjustmentObject.top === 0) shiftY = targetObject.spotlightAdjustment.top;
            if (adjustmentObject.width || adjustmentObject.width === 0) widthAdjust = targetObject.spotlightAdjustment.width;
            if (adjustmentObject.height || adjustmentObject.height === 0) heightAdjust = targetObject.spotlightAdjustment.height;
        }

        // set spotlight values
        $(tutorial.spotlightDiv).css({
            left: `${elemOffset.left + shiftX}px`,
            top: `${elemOffset.top + shiftY}px`,
            width: `${elemBCR.width + widthAdjust}px`,
            height: `${elemBCR.height + heightAdjust}px`,
            transition: (useInstantTransition)? '0s' : '0.3s ease-in-out'
        });

        // update veil divs
        tutorial.topVeil.style.left = `${elemBCR.x}px`;
        tutorial.topVeil.style.top = `0px`;
        tutorial.topVeil.style.width = `${elemBCR.width}px`;
        tutorial.topVeil.style.height = `${elemOffset.top}px`;

        tutorial.bottomVeil.style.left = `${elemBCR.x}px`;
        tutorial.bottomVeil.style.top = `${elemOffset.top + elemBCR.height}px`;
        tutorial.bottomVeil.style.width = `${elemBCR.width}px`;
        tutorial.bottomVeil.style.height = `${document.body.offsetHeight - (elemOffset.top + elemBCR.height)}px`;

        tutorial.leftVeil.style.left = `0px`;
        tutorial.leftVeil.style.top =  `0px`;
        tutorial.leftVeil.style.width = `${elemBCR.x}px`;
        tutorial.leftVeil.style.height = `${document.body.offsetHeight}px`;

        tutorial.rightVeil.style.left = `${elemBCR.x + elemBCR.width}px`;
        tutorial.rightVeil.style.right = '0px';
        tutorial.rightVeil.style.top = `0px`;
        tutorial.rightVeil.style.width = 'auto';
        tutorial.rightVeil.style.height = `${document.body.offsetHeight}px`;
    }


    /**
     * Updates checklist if necessary.
     * Also where user-added onSpotlightEnd code runs.  
     * 
     * @param direction Specifies whether "Next" or "Previous" was selected.
     */ 
    tutorial.postSpotlightProcessing = function(direction) {

        const targetObject = tutorial.currentSpotlightTarget;

        // if tutorial is active, disable tooltip temporarily
        if (tutorial.isActive) {
            // hide and disable previous tooltip
            tutorial.tippyInstance.enable(); // need to enable in order to hide
            tutorial.tippyInstance.hide();
            tutorial.tippyInstance.disable();


            if (targetObject.customEventTarget) {
                const customEventTargetElement = document.querySelector(targetObject.customEventTarget);           
                customEventTargetElement.removeEventListener(targetObject.customEventType, tutorial.nextEventListener); 
            }

            // update progress bar
            //tutorial.updateChecklistProgressBar();
        }

        // if provided (defined), run user-defined onSpotlightEnd function for spotlight
        if (targetObject.onSpotlightEnd) {
            targetObject.onSpotlightEnd();
        }

        switch (direction) {
            case "next":
                tutorial.stepHistoryStack.push(targetObject);
                break;

            case "previous":
                tutorial.stepStack.push(targetObject);
                break;
        }

        // if spotlight is a checklist item, update checklist (cross-off that item)
        if (targetObject.checklistText) {
            // if needed, dynamically scroll down the checklist so completed step is visible
            /*
            let scrollTop = tutorial.checklistItemsContainer.scrollTop;
            let elemOffsetTop = $(`#${spotlightObject.checklistId}`)[0].offsetTop;
            if ((elemOffsetTop - scrollTop) > 240) {
                tutorial.checklistItemsContainer.scroll({
                    left: 0, 
                    top: elemOffsetTop - 110, 
                    behavior: 'smooth'
                });
            }
            
            $(`#${spotlightObject.checklistCheckmarkId}`)[0].setAttribute('fill', '#68cc74');
            */
        }
    }


    /**
     * Hide tutorial.
     * 
     * Note: closing a tutorial is different from finishing a tutorial.
     * How is it different? LocalStorage are not updated and index is not reset
     * To think about: should tutorial be shown if user refreshes page?
     */
    tutorial.close = function() {
        // turn off mutation observer
        tutorial.mutationObserver.disconnect();
        // remove event listeners
        window.removeEventListener('resize', tutorial.recalculatePositions);
        document.removeEventListener('scroll', tutorial.recalculatePositions);
        document.body.removeEventListener('click', tutorial.onClick);

        // hide and disable all tutorial tippy
        tutorial.tippyInstance.enable();
        tutorial.tippyInstance.hide();
        tutorial.tippyInstance.disable();

        tutorial.isActive = false;
        document.body.removeChild(tutorial.spotlightDiv);
        //document.body.removeChild(tutorial.checkListDiv);
        document.body.removeChild(tutorial.centerDialogDiv);
        let veilDivs = document.querySelectorAll('.tutorial-veil');
        for (let i=veilDivs.length-1; i>=0; i--) {
            let veilDiv = veilDivs[i];
            document.body.removeChild(veilDiv);
        }
    }


    /**
     * Close and finish tutorial.
     * 
     * Updates localStorage to specify that this tutorial has been completed. (DOES NOT DO THIS YET)
     */
    tutorial.finish = function() {

        tutorial.close();
        // set localStorage for this tutorial.
        tutorial.setLocalStorage({ isActive: false });

        // if (tutorial.settings.nextTutorial) {
        //     // Set localStorage for next tutorial.
        //     tutorial.setLocalStorage({ 
        //         tutorialName: tutorial.settings.nextTutorial.name,
        //         isActive: true,
        //     });
        //     window.location.href = tutorial.settings.nextTutorial.url;
        // }
    }


    /**
     * Updates the tutorial stacks that are storged in localStorage.
     * 
     * @param options Optional parameter. Allows you to specify certain metadata to set for 
     *                this tutorial, such as whether is has been completed.
     */
    tutorial.setLocalStorage = function(options) {
        let cachedDataObject = JSON.parse(window.localStorage.getItem('spotlight-data'));

        // Check for options that should modify data to be saved locally.
        const stepStack = (options?.isActive)? [...tutorial.stepStack, tutorial.currentSpotlightTarget] : tutorial.stepStack;
        const stepHistoryStack = (options?.isActive)? tutorial.stepHistoryStack : [];
        const isActive = (options?.isActive)? true : false;

        const tutorialName = (options?.tutorialName)? options.tutorialName : tutorial.settings.tutorialName;
        
        cachedDataObject[tutorialName] = {
            "stepStack": stepStack,
            "stepHistoryStack": stepHistoryStack,
            "isActive": isActive,
        };
        window.localStorage.setItem('spotlight-data', JSON.stringify(cachedDataObject));
    }


    /**
     * Generate unique IDs for every spotlight object.
     * These IDs are used to match and identify spotlight data that is loaded from localStorage.
     * 
     * @param steps Specifies the Step objects that the IDs should be generated for.
     * @param rootId Specifies an ID that will be used as a prefix when generating new IDs
     *               Example: if rootId = '1.2', generated IDs will have format 
     *               '< tutorial-name >[1.2.< generated-number >]'
     */
    tutorial.generateStepIds = function(steps, rootId) {

        // Loop through all steps in tutorial and process them properly by either setting
        // the IDs of Spotlight objects, or making recursive calls on Fork and
        // Tutorial objects to set IDs of Spotlight objects inside them.
        for (let i=0; i<steps.length; i++) {
            const step = steps[i];

            switch(step.type) {

                // Step type Fork: Make recursive call for each branch option
                // to set IDs of steps in each branch.
                case 'fork':

                    // Set ID for Fork object
                    step.id = `${tutorial.settings.tutorialName}[${i}]`;

                    // Set IDs for every branch in the Fork
                    for (let j=0; j<step.branches.length; j++) {
                        // Generate new root IDs for each branch.
                        const newRootId = (rootId)? `${rootId}.${i}.${j}` : `${i}.${j}`;
                        step.branches[j].id = `${tutorial.settings.tutorialName}[${newRootId}]`;
                        tutorial.generateStepIds(step.branches[j].steps, newRootId);
                    }
                    break;

                // Step type Tutorial: Make recursive call to set IDs of steps in Tutorial.
                case 'tutorial':
                    // Set ID for Tutorial object
                    // step.id = `${tutorial.settings.tutorialName}[${i}]`;

                    // // Generate new root ID for tutorial.
                    // const newRootId = (rootId)? `${rootId}.${i}` : i;
                    // tutorial.generateStepIds(step.tutorial.steps, newRootId);
                    break;

                // Step type Spotlight (default): Set spotlight ID.
                // If type is not provided, type Spotlight is assumed.
                default:
                    // Check if a rootId has been provided.
                    if (rootId) step.id = `${tutorial.settings.tutorialName}[${rootId}.${i}]`
                    else step.id =  `${tutorial.settings.tutorialName}[${i}]`;
            }
        }
    }


    /**
     * Reconstruct the stepStack and stepHistoryStack based on data stored in localStorage.
     * 
     * @param {array} localStepStack localStorage data for stepStack
     * @param {array} localStepHistoryStack localStorage data for stepHistoryStack
     */
    tutorial.reconstructStacksFromLocalStorage = function(localStepHistoryStack) {
        // Regex matches any sequence that has format: [1.24.5 etc.]
        // used for processing and comparing Step IDs.
        const regex = /\[\d+((\.\d+)+)?\]/;
        
        while (localStepHistoryStack.length > 0) {

            const nextStep = tutorial.stepStack.pop();
            const nextLocalHistStep = localStepHistoryStack[0];

            switch(nextStep.type) {
                case 'fork':
                    const fork = nextStep;                   
                    for (let i=0; i<fork.branches.length; i++) {            
                        const branch = fork.branches[i];
                        if (branch.steps[0].id === nextLocalHistStep.id) {
                            for (let j=0; j<branch.steps.length; j++) {
                                tutorial.stepStack.push(branch.steps[j]);
                            }                                         
                        }
                    }
                    break;

                case 'tutorial':

                    break;

                default:            
                    if (nextStep.id === nextLocalHistStep.id) {
                        tutorial.stepHistoryStack.push(nextStep);
                        // For most operations we use pop(), but here we use shift() because
                        // we want to retrieve the Spotlight from the top of the stack rather 
                        // than from the end.
                        localStepHistoryStack.shift();
                    }
            }
        }
    }


    /**
     * Event listener that runs in response to any action that should
     * trigger the appearance of the next Spotlight.
     */
    tutorial.nextEventListener = function() {
        tutorial.postSpotlightProcessing("next");
        tutorial.next();
    };

    
    /**
     * Event listener that runs in response to any action that should
     * trigger the appearance of the previous Spotlight.
     */
    tutorial.previousEventListener = function() {
        tutorial.postSpotlightProcessing("previous");
        tutorial.previous();
    }


    //**  DEPRECATED METHODS START **//

    /**
     * Updates the progress bar in the tutorial checklist
     * 
     * @param percent optional percent value to set the progress bar to
     */
    tutorial.updateChecklistProgressBar = function(percent) {
        percent = (percent)? percent : (tutorial.tutorialLength > 0) ? ((tutorial.tutorialIndex)/tutorial.tutorialLength)*100 : 0;
        let percentProgress = percent;
        $('#checklist-progress-bar')[0].style.width = `${percentProgress}%`;
    }


    /**
     * Function that gets run when user clicks on tutorial veil (does not currently get run).
     * 
     * @param e JS event object.
     * @param goToPrev Specifies whether user should be taken to previous spotlight.
     */
     tutorial.onClick = function(e, goToPrev) {
        if(!(tutorial.steps[tutorial.tutorialIndex].deactivatePrevBtn === true) && (e.shiftKey || goToPrev)) {
            tutorial.previous();
            return;
        }   
        if (!(tutorial.steps[tutorial.tutorialIndex].deactivateNextBtn === true)) tutorial.next();
    }

    //**  DEPRECATED METHODS END **//

    // setup tutorial and return tutorial instance
    tutorial.setup();
    return tutorial;
}
