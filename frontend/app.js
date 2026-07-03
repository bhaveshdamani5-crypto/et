let pollInterval = null;
let currentIssue = null;

window.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('/api/state');
        const data = await response.json();
        if (data.active_issues && data.active_issues.length > 0) {
            currentIssue = data.active_issues[data.active_issues.length - 1];
            document.getElementById('issue-input').value = currentIssue;
            
            if (data.latest_results) {
                renderAllDashboards(data.latest_results);
            }
            startPolling();
        }
    } catch(err) {
        console.error("No historical state found.", err);
    }
});

function startPolling() {
    if (!pollInterval) {
        pollInterval = setInterval(async () => {
            try {
                const response = await fetch('/api/state');
                const data = await response.json();
                if (data.latest_results) {
                    renderAllDashboards(data.latest_results);
                }
            } catch(err) {
                console.error("Background sync failed:", err);
            }
        }, 120000); // 2 minutes auto-refresh exactly as requested!
    }
}

document.getElementById('run-sim-btn').addEventListener('click', async () => {
    const issueInput = document.getElementById('issue-input').value.trim();
    if (!issueInput) {
        alert("Please enter a global issue to monitor.");
        return;
    }

    currentIssue = issueInput;
    const btn = document.getElementById('run-sim-btn');
    btn.disabled = true;
    btn.innerText = "Analyzing...";
    
    const badge = document.getElementById('status-badge');
    if (badge) {
        badge.className = 'status badge-running';
        badge.innerText = 'FETCHING NEW DATA...';
    }

    try {
        const response = await fetch('/api/simulate', { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ issue_query: issueInput })
        });
        
        if (!response.ok) throw new Error("API Request Failed");
        const data = await response.json();
        
        // Fetch all state again to render all issues including the new one
        const stateRes = await fetch('/api/state');
        const stateData = await stateRes.json();
        if (stateData.latest_results) {
            renderAllDashboards(stateData.latest_results);
        }
        
        startPolling();
    } catch (err) {
        console.error(err);
        if (badge) {
            badge.className = 'status badge-pending';
            badge.innerText = 'ERROR';
        }
    } finally {
        btn.disabled = false;
        btn.innerText = "Analyze Global Risk";
    }
});

async function stopAgent(issueToStop) {
    await fetch('/api/stop', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ issue_query: issueToStop })
    });
    
    const response = await fetch('/api/state');
    const data = await response.json();
    if (data.latest_results && Object.keys(data.latest_results).length > 0) {
        renderAllDashboards(data.latest_results);
    } else {
        document.getElementById('body-watchtower').innerHTML = '<p style="color:#9ca3af; text-align:center;">All agents stopped. Enter a new issue to monitor.</p>';
        document.getElementById('status-badge').className = 'status badge-pending';
        document.getElementById('status-badge').innerText = 'STOPPED';
        currentIssue = null;
    }
}

function renderAllDashboards(latest_results) {
    if (!latest_results || Object.keys(latest_results).length === 0) return;
    
    const card = document.getElementById('card-watchtower');
    const badge = document.getElementById('status-badge');
    const body = document.getElementById('body-watchtower');
    
    card.classList.add('active');
    badge.className = 'status badge-done';
    badge.innerText = 'LIVE MONITORING - NATIONAL COMMAND CENTER';

    let allHtml = "";
    const issues = Object.keys(latest_results).reverse(); // Newest first
    
    for (const issue of issues) {
        let w_data_raw = latest_results[issue];
        if (!w_data_raw) continue;
        
        // Handle new Hybrid Integration JSON format where watchtower output is nested in 'data'
        const w_data = w_data_raw.data || w_data_raw;
        
        const ex = w_data.executive_summary;
        const fusion = w_data.intelligence_fusion;
        const signals = w_data.signals || [];
        const impact = w_data.impact_assessment;
        
        let riskColor = ex.disruption_probability >= 80 ? '#DC2626' : ex.disruption_probability >= 60 ? '#EA580C' : '#CA8A04';
        const canvasId = 'chart_' + issue.replace(/[^a-zA-Z0-9]/g, '_');
        
        // Categorize LLM Signals into the 6 sections
        const geoSignals = signals.filter(s => ['military_escalation', 'diplomatic_tension', 'geopolitical_tension'].includes(s.event_type));
        const finSignals = signals.filter(s => ['economic_policy', 'financial_market'].includes(s.event_type));
        const logSignals = signals.filter(s => ['trade_disruption', 'energy_infrastructure', 'logistics'].includes(s.event_type));
        const socSignals = signals.filter(s => ['sanctions', 'social_unrest', 'policy'].includes(s.event_type));
        const cyberSignals = signals.filter(s => ['cyber_attack', 'emerging_tech'].includes(s.event_type));
        const weatherSignals = signals.filter(s => ['natural_disaster', 'climate'].includes(s.event_type));

        // Fallback unmapped signals to Geopolitical
        signals.forEach(s => {
            if (!geoSignals.includes(s) && !finSignals.includes(s) && !logSignals.includes(s) && !socSignals.includes(s) && !cyberSignals.includes(s) && !weatherSignals.includes(s)) {
                geoSignals.push(s);
            }
        });

        allHtml += `
            <div style="background: #0f1115; border-radius: 12px; padding: 1.5rem; border: 1px solid #1f2937; margin-bottom: 40px; position: relative;">
                <button onclick="stopAgent('${issue}')" style="position: absolute; top: 15px; right: 15px; background: #7f1d1d; color: white; border: 1px solid #b91c1c; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 0.75rem; font-weight: bold; letter-spacing: 1px;">TERMINATE LINK</button>
                
                <!-- TOP EXECUTIVE DASHBOARD -->
                <div style="margin-bottom: 2rem; padding-bottom: 1.5rem; border-bottom: 1px solid #1f2937;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                        <h1 style="color: white; font-size: 1.5rem; font-weight: 700; margin: 0; letter-spacing: 1px; text-transform: uppercase;">
                            🌐 ${w_data.report_metadata?.target_issue?.toUpperCase() || issue.toUpperCase()} - NATIONAL SECURITY BRIEF
                        </h1>
                    </div>
                    
                    <div style="display: flex; gap: 20px; align-items: center; margin-bottom: 1.5rem;">
                        <div style="background: rgba(255,255,255,0.05); padding: 10px 20px; border-radius: 6px; border-left: 4px solid ${riskColor};">
                            <div style="color: #9ca3af; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px;">Threat Level</div>
                            <div style="color: white; font-size: 1.25rem; font-weight: bold;">${ex.threat_level}</div>
                        </div>
                        <div style="background: rgba(255,255,255,0.05); padding: 10px 20px; border-radius: 6px; border-left: 4px solid #3b82f6;">
                            <div style="color: #9ca3af; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px;">Disruption Probability</div>
                            <div style="color: white; font-size: 1.25rem; font-weight: bold;">${ex.disruption_probability}%</div>
                        </div>
                        <div style="background: rgba(255,255,255,0.05); padding: 10px 20px; border-radius: 6px; border-left: 4px solid #10b981;">
                            <div style="color: #9ca3af; font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px;">Last AI Sync</div>
                            <div style="color: white; font-size: 1.25rem; font-weight: bold;">${new Date().toLocaleTimeString()}</div>
                        </div>
                    </div>

                    <div style="padding: 15px; background: rgba(59, 130, 246, 0.1); border-left: 3px solid #3b82f6; font-size: 0.85rem; color: #e5e7eb; line-height: 1.5;">
                        <strong style="color: #60a5fa;">NVIDIA AI EXECUTIVE ASSESSMENT:</strong> ${ex.assessment}
                    </div>
                </div>

                <!-- 6 SECTION GOVERNMENT GRID -->
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px;">
                    
                    <!-- SECTION 1: GEOPOLITICAL -->
                    <div class="gov-section" style="background: #111827; border: 1px solid #374151; border-radius: 8px; padding: 15px;">
                        <h3 style="color: #93c5fd; font-size: 0.9rem; margin-top: 0; margin-bottom: 15px; display: flex; align-items: center; gap: 8px; border-bottom: 1px solid #1f2937; padding-bottom: 8px;">
                            🌍 Geopolitical Intelligence
                        </h3>
                        ${renderSignalsGrid(geoSignals)}
                    </div>

                    <!-- SECTION 2: FINANCIAL & ECONOMIC -->
                    <div class="gov-section" style="background: #111827; border: 1px solid #374151; border-radius: 8px; padding: 15px;">
                        <h3 style="color: #fcd34d; font-size: 0.9rem; margin-top: 0; margin-bottom: 15px; display: flex; align-items: center; gap: 8px; border-bottom: 1px solid #1f2937; padding-bottom: 8px;">
                            💰 Financial & Economic Intelligence
                        </h3>
                        ${fusion?.financial_and_trade?.oil_options_flow?.status === "success" ? `
                            <div style="background: #000; padding: 10px; border-radius: 6px; border: 1px solid #374151; margin-bottom: 15px;">
                                <div style="color: #9ca3af; font-size: 0.7rem; margin-bottom: 5px; text-transform: uppercase;">Live Brent Crude Spot Graph</div>
                                <canvas id="${canvasId}" width="400" height="120" style="width: 100%; height: 120px;"></canvas>
                            </div>
                        ` : ''}
                        ${renderSignalsGrid(finSignals)}
                    </div>

                    <!-- SECTION 3: WEATHER & EMERGENCY -->
                    <div class="gov-section" style="background: #111827; border: 1px solid #374151; border-radius: 8px; padding: 15px;">
                        <h3 style="color: #67e8f9; font-size: 0.9rem; margin-top: 0; margin-bottom: 15px; display: flex; align-items: center; gap: 8px; border-bottom: 1px solid #1f2937; padding-bottom: 8px;">
                            🌦 Weather, Climate & Emergency
                        </h3>
                        ${(() => {
                            const allCP = fusion?.weather_and_disasters?.openweather?.all_chokepoints;
                            if (allCP && allCP.length > 0) {
                                return '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 15px;">' +
                                    allCP.map(cp => {
                                        const icon = cp.condition === 'Clear' ? '☀️' : cp.condition === 'Clouds' ? '☁️' : cp.condition === 'Rain' ? '🌧️' : cp.condition === 'Thunderstorm' ? '⛈️' : '🌤️';
                                        const color = cp.condition === 'Clear' ? '#34d399' : cp.condition === 'Rain' || cp.condition === 'Thunderstorm' ? '#f87171' : '#fbbf24';
                                        return '<div style="background: rgba(17,24,39,0.8); border: 1px solid #374151; border-radius: 6px; padding: 10px;">' +
                                            '<div style="font-size: 0.7rem; color: #9ca3af; text-transform: uppercase; margin-bottom: 4px;">' + icon + ' ' + cp.chokepoint + '</div>' +
                                            '<div style="font-size: 0.85rem; color: ' + color + '; font-weight: bold;">' + cp.condition + '</div>' +
                                            '<div style="font-size: 0.65rem; color: #6b7280; margin-top: 2px;">Wind: ' + (cp.wind_speed_m_s || 0) + ' m/s | ' + (cp.temp_celsius || 'N/A') + '°C</div>' +
                                        '</div>';
                                    }).join('') +
                                '</div>';
                            } else if (fusion?.weather_and_disasters?.openweather?.chokepoint) {
                                return '<div style="padding: 10px; background: rgba(103,232,249,0.1); border-left: 3px solid #67e8f9; font-size: 0.75rem; color: #d1d5db; margin-bottom: 15px;">' +
                                    '<strong>' + fusion.weather_and_disasters.openweather.chokepoint + ':</strong> ' + fusion.weather_and_disasters.openweather.condition +
                                '</div>';
                            }
                            return '';
                        })()}
                        ${renderSignalsGrid(weatherSignals)}
                    </div>

                    <!-- SECTION 4: LOGISTICS & SUPPLY CHAIN -->
                    <div class="gov-section" style="background: #111827; border: 1px solid #374151; border-radius: 8px; padding: 15px;">
                        <h3 style="color: #fdba74; font-size: 0.9rem; margin-top: 0; margin-bottom: 15px; display: flex; align-items: center; gap: 8px; border-bottom: 1px solid #1f2937; padding-bottom: 8px;">
                            🚢 Logistics, Trade & Supply Chain
                        </h3>
                        ${fusion?.satellite?.nasa_firms?.critical_anomalies_detected ? `
                            <div style="margin-bottom: 15px;">
                                <img src="${fusion.satellite.nasa_firms.image_url || 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=400&auto=format&fit=crop'}" style="width: 100%; height: 120px; object-fit: cover; border-radius: 6px; border: 1px solid #374151;">
                                <div style="font-size: 0.75rem; color: #d1d5db; margin-top: 5px;">🛰️ <strong>NASA FIRMS:</strong> Critical thermal anomaly detected in logistics corridor.</div>
                            </div>
                        ` : ''}
                        ${renderSignalsGrid(logSignals)}
                    </div>

                    <!-- SECTION 5: SOCIAL, POLICY & GOV -->
                    <div class="gov-section" style="background: #111827; border: 1px solid #374151; border-radius: 8px; padding: 15px;">
                        <h3 style="color: #d8b4fe; font-size: 0.9rem; margin-top: 0; margin-bottom: 15px; display: flex; align-items: center; gap: 8px; border-bottom: 1px solid #1f2937; padding-bottom: 8px;">
                            👥 Social, Policy & Government
                        </h3>
                        ${fusion?.social?.telegram?.signals_detected ? `
                            <div style="padding: 10px; background: rgba(59, 130, 246, 0.1); border-left: 3px solid #3b82f6; font-size: 0.75rem; color: #d1d5db; margin-bottom: 15px;">
                                <strong>TELEGRAM INTEL:</strong> High volume of insider military/social chatter detected in regional groups.
                            </div>
                        ` : ''}
                        ${renderSignalsGrid(socSignals)}
                    </div>

                    <!-- SECTION 6: CYBERSECURITY & TECH -->
                    <div class="gov-section" style="background: #111827; border: 1px solid #374151; border-radius: 8px; padding: 15px;">
                        <h3 style="color: #fca5a5; font-size: 0.9rem; margin-top: 0; margin-bottom: 15px; display: flex; align-items: center; gap: 8px; border-bottom: 1px solid #1f2937; padding-bottom: 8px;">
                            🔐 Cybersecurity & Emerging Tech
                        </h3>
                        ${fusion?.cyber?.shodan?.status === "success" && fusion.cyber.shodan.data?.total_exposed_scada_systems > 0 ? `
                            <div style="padding: 10px; background: rgba(239, 68, 68, 0.1); border-left: 3px solid #ef4444; font-size: 0.75rem; color: #d1d5db; margin-bottom: 15px;">
                                <strong>SHODAN SCAN:</strong> ${fusion.cyber.shodan.data.total_exposed_scada_systems} exposed ICS/SCADA critical infrastructure systems found vulnerable in target region.
                            </div>
                        ` : ''}
                        ${renderSignalsGrid(cyberSignals)}
                    </div>

                </div>
                
                ${ex.disruption_probability >= 70 ? `
                    <div style="background: rgba(127, 29, 29, 0.2); border: 1px solid #b91c1c; border-radius: 8px; padding: 15px; margin-top: 20px;">
                        <div style="color: #fca5a5; font-weight: bold; font-size: 0.9rem; margin-bottom: 0.5rem;">⚠️ COMMANDER AGENT ACTIVATION RECOMMENDED</div>
                        <div style="color: #d1d5db; font-size: 0.8rem;">
                            <strong>Projected Impact:</strong> ${impact?.supply_gap_mbpd} MBPD Supply Gap | ₹${impact?.economic_impact?.fiscal_loss_rs_crore} Cr Est. Fiscal Loss<br>
                            <em>System recommends immediate activation of emergency SPR protocols.</em>
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }

    body.innerHTML = allHtml;

    // Draw all graphs after inserting HTML
    for (const issue of issues) {
        const w_data = latest_results[issue];
        if (w_data?.intelligence_fusion?.financial_and_trade?.stock_history) {
            const canvasId = 'chart_' + issue.replace(/[^a-zA-Z0-9]/g, '_');
            drawNativeGraph(canvasId, w_data.intelligence_fusion.financial_and_trade.stock_history);
        }
    }
}

// Helper to render AI signals in each grid cell
function renderSignalsGrid(signalsArray) {
    if (!signalsArray || signalsArray.length === 0) {
        return `<div style="color: #6b7280; font-size: 0.75rem; font-style: italic;">No critical AI anomalies detected in this sector.</div>`;
    }
    
    let out = `<div style="display: flex; flex-direction: column; gap: 10px;">`;
    signalsArray.forEach((sig) => {
        const uniqueId = `ai-expand-${Math.random().toString(36).substr(2, 9)}`;
        const sev = parseInt(sig.severity || 5);
        const color = sev >= 8 ? '#ef4444' : sev >= 5 ? '#f59e0b' : '#3b82f6';
        
        out += `
            <div style="background: rgba(255,255,255,0.03); border: 1px solid #374151; border-radius: 6px; padding: 10px; cursor: pointer; transition: background 0.2s;" onclick="document.getElementById('${uniqueId}').style.display = document.getElementById('${uniqueId}').style.display === 'none' ? 'block' : 'none';">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 5px;">
                    <strong style="color: #e5e7eb; font-size: 0.75rem; text-transform: uppercase;">
                        <span style="display:inline-block; width:8px; height:8px; background:${color}; border-radius:50%; margin-right:5px;"></span>
                        ${sig.event_type ? sig.event_type.replace(/_/g, ' ') : 'ALERT'}
                    </strong>
                    <span style="color: #6b7280; font-size: 0.65rem;">SEV: ${sev}/10 | Click to expand AI Analysis</span>
                </div>
                <p style="color: #9ca3af; font-size: 0.75rem; margin: 0; line-height: 1.4;">${sig.description}</p>
                
                <div id="${uniqueId}" style="display: none; margin-top: 10px; padding-top: 10px; border-top: 1px dashed #374151; color: #a7f3d0; font-size: 0.75rem; line-height: 1.5;">
                    <div style="margin-bottom: 8px;">
                        ${sig.deep_explanation || sig.ai_deep_analysis || 'No detailed analysis provided.'}
                    </div>
                    <div style="margin-top: 8px; display: flex; gap: 15px; color: #6b7280;">
                        <span>📍 ${sig.impacted_region || 'Global'}</span>
                        <span>🎯 Conf: ${Math.round((sig.confidence || 0.8) * 100)}%</span>
                    </div>
                </div>
            </div>
        `;
    });
    out += `</div>`;
    return out;
}

function drawNativeGraph(canvasId, history) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const w = canvas.width;
    const h = canvas.height;
    ctx.clearRect(0, 0, w, h);
    
    ctx.strokeStyle = '#1f2937';
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (let i = 0; i < 4; i++) {
        let y = i * (h / 4);
        ctx.moveTo(0, y);
        ctx.lineTo(w, y);
    }
    ctx.stroke();

    const min = Math.min(...history) - 2;
    const max = Math.max(...history) + 2;
    const range = max - min;
    
    ctx.strokeStyle = '#fcd34d';
    ctx.lineWidth = 2;
    ctx.beginPath();
    history.forEach((val, i) => {
        const x = (i / (history.length - 1)) * w;
        const y = h - ((val - min) / range) * h;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });
    ctx.stroke();
    
    ctx.lineTo(w, h);
    ctx.lineTo(0, h);
    ctx.fillStyle = 'rgba(252, 211, 77, 0.1)';
    ctx.fill();
    
    const latestPrice = history[history.length - 1];
    ctx.fillStyle = '#fcd34d';
    ctx.font = "bold 11px Inter, sans-serif";
    ctx.fillText("LIVE: $" + latestPrice.toFixed(2), w - 80, 20);
}
