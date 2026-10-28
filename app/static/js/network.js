// Vis.js Interactive Team Compatibility Network

document.addEventListener('DOMContentLoaded', function () {
    const container = document.getElementById('network-vis');
    if (!container) return;

    let network = null;
    let allNodes = [];

    function loadNetwork(skillFilter = '', interestFilter = '') {
        const url = `/api/network-data?skill=${encodeURIComponent(skillFilter)}&interest=${encodeURIComponent(interestFilter)}`;

        fetch(url)
            .then(res => res.json())
            .then(data => {
                allNodes = data.nodes;

                const nodes = new vis.DataSet(data.nodes.map(n => ({
                    id: n.id,
                    label: n.label,
                    title: n.title,
                    color: {
                        background: n.color,
                        border: '#1e293b',
                        highlight: { background: '#2563eb', border: '#1d4ed8' }
                    },
                    font: { color: '#0f172a', size: 12, face: 'Inter' },
                    shape: 'dot',
                    size: 16
                })));

                const edges = new vis.DataSet(data.edges.map(e => ({
                    id: e.id,
                    from: e.from,
                    to: e.to,
                    value: e.value,
                    color: { color: '#cbd5e1', highlight: '#2563eb' },
                    title: e.title
                })));

                const networkData = { nodes: nodes, edges: edges };

                const options = {
                    nodes: {
                        borderWidth: 1.5,
                        shadow: true
                    },
                    edges: {
                        smooth: { type: 'continuous' }
                    },
                    physics: {
                        stabilization: true,
                        barnesHut: {
                            gravitationalConstant: -3000,
                            springConstant: 0.04,
                            springLength: 95
                        }
                    },
                    interaction: {
                        hover: true,
                        tooltipDelay: 100
                    }
                };

                network = new vis.Network(container, networkData, options);

                // Click node event to display student slide-out card
                network.on('click', function (params) {
                    if (params.nodes.length > 0) {
                        const nodeId = params.nodes[0];
                        const studentObj = allNodes.find(n => n.id === nodeId);
                        if (studentObj) {
                            displayStudentCard(studentObj);
                        }
                    }
                });
            })
            .catch(err => {
                container.innerHTML = `<div class="p-4 text-danger">Error loading network data: ${err.message}</div>`;
            });
    }

    function displayStudentCard(s) {
        const cardContainer = document.getElementById('selected-student-card');
        if (!cardContainer) return;

        const skillsHtml = s.skills.map(sk => `<span class="badge badge-soft-primary me-1 mb-1">${sk}</span>`).join('');
        const interestsHtml = s.interests.map(it => `<span class="badge badge-soft-info me-1 mb-1">${it}</span>`).join('');

        cardContainer.innerHTML = `
            <div class="card border border-primary shadow-sm">
                <div class="card-header bg-primary bg-opacity-10 fw-semibold d-flex justify-content-between align-items-center">
                    <span>${s.label} (${s.department})</span>
                    <span class="badge" style="background-color: ${s.color}; color: #fff;">${s.team}</span>
                </div>
                <div class="card-body p-3 small">
                    <div class="mb-2"><strong>Experience:</strong> ${s.experience} Months</div>
                    <div class="mb-2"><strong>Preferred Roles:</strong> ${s.roles.join(', ') || 'Not specified'}</div>
                    <div class="mb-2">
                        <strong class="d-block mb-1">Skills:</strong>
                        ${skillsHtml || '<span class="text-muted">None</span>'}
                    </div>
                    <div class="mb-2">
                        <strong class="d-block mb-1">Interests:</strong>
                        ${interestsHtml || '<span class="text-muted">None</span>'}
                    </div>
                    <div class="mt-3">
                        <a href="/students/${s.id}" class="btn btn-outline-primary btn-sm py-0 px-2">Open Full Profile</a>
                    </div>
                </div>
            </div>
        `;
    }

    // Filter handlers
    const filterBtn = document.getElementById('apply-network-filter');
    if (filterBtn) {
        filterBtn.addEventListener('click', function () {
            const skVal = document.getElementById('net-skill-select').value;
            const intVal = document.getElementById('net-interest-select').value;
            loadNetwork(skVal, intVal);
        });
    }

    loadNetwork();
});
