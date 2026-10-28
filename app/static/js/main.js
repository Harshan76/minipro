// Common JavaScript for AI Group Project Team Builder

document.addEventListener('DOMContentLoaded', function () {
    // 1. Mobile sidebar toggle
    const toggleBtn = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener('click', function () {
            sidebar.classList.toggle('show');
        });
    }

    // 2. Initialize Bootstrap tooltips & popovers
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (el) {
        return new bootstrap.Tooltip(el);
    });

    // 3. Confirmation dialogs for critical actions
    document.querySelectorAll('[data-confirm]').forEach(function (element) {
        element.addEventListener('click', function (e) {
            const message = this.getAttribute('data-confirm') || 'Are you sure you want to proceed?';
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // 4. "Why This Team?" Modal Dynamic Fetch
    const whyModal = document.getElementById('whyThisTeamModal');
    if (whyModal) {
        whyModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const teamId = button.getAttribute('data-team-id');
            const modalTitle = whyModal.querySelector('.modal-title');
            const modalBody = whyModal.querySelector('#whyModalContent');

            modalTitle.textContent = `Why This Team Was Recommended`;
            modalBody.innerHTML = `
                <div class="text-center py-4">
                    <div class="spinner-border text-primary" role="status"></div>
                    <p class="mt-2 text-muted small">Generating plain English explanation from team profile patterns...</p>
                </div>
            `;

            fetch(`/teams/${teamId}/why?json=1`, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(res => res.json())
            .then(data => {
                let archetypesHtml = '';
                if (data.archetypes && data.archetypes.length > 0) {
                    archetypesHtml = data.archetypes.map(a => `
                        <div class="d-flex align-items-center justify-content-between p-2 mb-1 bg-light rounded border">
                            <span class="fw-medium">${a.student_name}</span>
                            <span class="badge badge-soft-primary">${a.archetype}</span>
                        </div>
                    `).join('');
                }

                let coveredHtml = '';
                if (data.covered_skills && data.covered_skills.length > 0) {
                    coveredHtml = data.covered_skills.map(s => `
                        <span class="badge badge-soft-success me-1 mb-1">
                            <i class="bi bi-check-circle me-1"></i>${s.name} (${s.proficiency} by ${s.provider})
                        </span>
                    `).join('');
                }

                let missingHtml = '';
                if (data.missing_skills && data.missing_skills.length > 0) {
                    missingHtml = data.missing_skills.map(s => `
                        <span class="badge badge-soft-warning me-1 mb-1">
                            <i class="bi bi-exclamation-triangle me-1"></i>${s.name} ${s.is_mandatory ? '(Mandatory)' : ''}
                        </span>
                    `).join('');
                } else {
                    missingHtml = '<span class="text-success small"><i class="bi bi-check-all me-1"></i>All required skills covered!</span>';
                }

                let suggestionsHtml = '';
                if (data.suggestions && data.suggestions.length > 0) {
                    suggestionsHtml = data.suggestions.map(sg => `
                        <li class="mb-1 text-muted small">${sg}</li>
                    `).join('');
                }

                let sharedDaysHtml = data.shared_days && data.shared_days.length > 0
                    ? `<span class="badge badge-soft-info">${data.shared_days.join(', ')}</span>`
                    : `<span class="text-muted small">No mutual single day (Asynchronous collaboration recommended)</span>`;

                modalBody.innerHTML = `
                    <div class="alert alert-primary bg-primary bg-opacity-10 border-primary border-opacity-25 mb-3">
                        <div class="d-flex gap-2">
                            <i class="bi bi-stars text-primary fs-5"></i>
                            <div>
                                <h6 class="fw-bold mb-1 text-primary">Summary Explanation</h6>
                                <p class="mb-0 small text-dark">${data.summary_narrative}</p>
                            </div>
                        </div>
                    </div>

                    <div class="mb-3">
                        <h6 class="fw-semibold small text-uppercase text-muted">Discovered Profile Archetypes</h6>
                        <div>${archetypesHtml}</div>
                    </div>

                    <div class="mb-3">
                        <h6 class="fw-semibold small text-uppercase text-muted">Project Skills Coverage</h6>
                        <div class="mb-2">${coveredHtml}</div>
                        <div>
                            <span class="text-muted small fw-medium">Missing / Attention Needed:</span><br>
                            ${missingHtml}
                        </div>
                    </div>

                    <div class="mb-3">
                        <h6 class="fw-semibold small text-uppercase text-muted">Mutual Availability Overlap</h6>
                        <div>${sharedDaysHtml}</div>
                    </div>

                    <div class="mb-2">
                        <h6 class="fw-semibold small text-uppercase text-muted">Actionable Recommendations</h6>
                        <ul class="ps-3 mb-0">${suggestionsHtml}</ul>
                    </div>

                    <div class="accordion mt-3" id="techAccordion">
                        <div class="accordion-item border">
                            <h2 class="accordion-header" id="headingTech">
                                <button class="accordion-button collapsed py-2 small" type="button" data-bs-toggle="collapse" data-bs-target="#collapseTech">
                                    <i class="bi bi-code-slash me-2"></i>Technical Details (For Faculty / Evaluators)
                                </button>
                            </h2>
                            <div id="collapseTech" class="accordion-collapse collapse" data-bs-parent="#techAccordion">
                                <div class="accordion-body bg-light small">
                                    <pre class="mb-0" style="font-size: 0.75rem;">${JSON.stringify(data.technical_details, null, 2)}</pre>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            })
            .catch(err => {
                modalBody.innerHTML = `<div class="alert alert-danger">Error loading explanation: ${err.message}</div>`;
            });
        });
    }
});
