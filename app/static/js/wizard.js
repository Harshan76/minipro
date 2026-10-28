// Project Creation Wizard Multi-step Handler

document.addEventListener('DOMContentLoaded', function () {
    let currentStep = 1;
    const totalSteps = 4;

    const btnNext = document.getElementById('wizard-next');
    const btnPrev = document.getElementById('wizard-prev');
    const btnSubmit = document.getElementById('wizard-submit');

    function updateWizardView() {
        // Toggle step contents
        document.querySelectorAll('.wizard-step-pane').forEach((pane, idx) => {
            if (idx + 1 === currentStep) {
                pane.classList.remove('d-none');
            } else {
                pane.classList.add('d-none');
            }
        });

        // Update step indicators
        document.querySelectorAll('.wizard-indicator-step').forEach((ind, idx) => {
            ind.classList.remove('active', 'completed');
            if (idx + 1 < currentStep) {
                ind.classList.add('completed');
            } else if (idx + 1 === currentStep) {
                ind.classList.add('active');
            }
        });

        // Prev button visibility
        if (currentStep === 1) {
            btnPrev.classList.add('d-none');
        } else {
            btnPrev.classList.remove('d-none');
        }

        // Next vs Submit visibility
        if (currentStep === totalSteps) {
            btnNext.classList.add('d-none');
            btnSubmit.classList.remove('d-none');
            populateSummary();
        } else {
            btnNext.classList.remove('d-none');
            btnSubmit.classList.add('d-none');
        }
    }

    function validateCurrentStep() {
        if (currentStep === 1) {
            const title = document.getElementById('proj_title').value.trim();
            const desc = document.getElementById('proj_desc').value.trim();
            if (!title) {
                alert('Please enter a Project Title.');
                return false;
            }
            if (!desc) {
                alert('Please enter a brief Project Description.');
                return false;
            }
        } else if (currentStep === 2) {
            const checkedSkills = document.querySelectorAll('input[name="skills[]"]:checked');
            if (checkedSkills.length === 0) {
                alert('Please select at least 1 required technical skill for the project.');
                return false;
            }
        }
        return true;
    }

    function populateSummary() {
        const title = document.getElementById('proj_title').value.trim();
        const desc = document.getElementById('proj_desc').value.trim();
        const domain = document.getElementById('proj_domain').value.trim();
        const teamSize = document.getElementById('proj_size').value;
        const minHours = document.getElementById('proj_hours').value;
        const minExp = document.getElementById('proj_exp').value;

        document.getElementById('sum_title').textContent = title || 'Untitled Project';
        document.getElementById('sum_domain').textContent = domain || 'Web Development';
        document.getElementById('sum_desc').textContent = desc || 'No description provided.';
        document.getElementById('sum_size').textContent = `${teamSize} Students (Min: ${document.getElementById('proj_min_size').value}, Max: ${document.getElementById('proj_max_size').value})`;
        document.getElementById('sum_hours').textContent = `${minHours} Hours / Week`;
        document.getElementById('sum_exp').textContent = `${minExp} Months minimum`;

        // Skills summary
        const skillsContainer = document.getElementById('sum_skills');
        skillsContainer.innerHTML = '';
        document.querySelectorAll('input[name="skills[]"]:checked').forEach(cb => {
            const skId = cb.value;
            const skName = cb.getAttribute('data-skill-name') || 'Skill';
            const prof = document.querySelector(`select[name="prof_${skId}"]`).value;
            const isMandatory = document.querySelector(`select[name="mandatory_${skId}"]`).value === '1';

            const badge = document.createElement('span');
            badge.className = `badge ${isMandatory ? 'badge-soft-danger' : 'badge-soft-primary'} me-1 mb-1 p-2`;
            badge.innerHTML = `<i class="bi ${isMandatory ? 'bi-shield-lock' : 'bi-check'} me-1"></i>${skName} (${prof})${isMandatory ? ' [Mandatory]' : ' [Preferred]'}`;
            skillsContainer.appendChild(badge);
        });

        // Roles summary
        const rolesContainer = document.getElementById('sum_roles');
        rolesContainer.innerHTML = '';
        document.querySelectorAll('input[name="roles[]"]:checked').forEach(cb => {
            const badge = document.createElement('span');
            badge.className = 'badge badge-soft-purple me-1 mb-1 p-2';
            badge.textContent = cb.value;
            rolesContainer.appendChild(badge);
        });
    }

    if (btnNext) {
        btnNext.addEventListener('click', function () {
            if (validateCurrentStep()) {
                currentStep = Math.min(currentStep + 1, totalSteps);
                updateWizardView();
            }
        });
    }

    if (btnPrev) {
        btnPrev.addEventListener('click', function () {
            currentStep = Math.max(currentStep - 1, 1);
            updateWizardView();
        });
    }

    // Step indicators clickable for visited steps
    document.querySelectorAll('.wizard-indicator-step').forEach((ind, idx) => {
        ind.addEventListener('click', () => {
            if (idx + 1 < currentStep) {
                currentStep = idx + 1;
                updateWizardView();
            }
        });
    });

    updateWizardView();
});
