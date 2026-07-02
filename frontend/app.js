document.getElementById('run-sim-btn').addEventListener('click', async () => {
    const issueInput = document.getElementById('issue-input').value.trim();
    if (!issueInput) {
        alert("Please enter a global issue to monitor (e.g., 'Taiwan Blockade').");
        return;
    }

    const btn = document.getElementById('run-sim-btn');
    btn.disabled = true;
    btn.innerText = "Analyzing...";

    const card = document.getElementById('card-watchtower');
    const badge = document.getElementById('status-badge');
    const body = document.getElementById('body-watchtower');

    card.classList.add('active');
    badge.className = 'status badge-running';
    badge.innerText = 'MONITORING CYCLE...';
    body.innerHTML = `
        <div style="display:flex; justify-content:center; align-items:center; height:150px;">
            <div style="text-align:center;">
                <div class="pulse" style="margin: 0 auto 15px auto; width: 20px; height: 20px;"></div>
                <p>Analyzing geopolitical risk data...</p>
            </div>
        </div>
    `;

    try {
        const response = await fetch('/api/simulate', { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ issue_query: issueInput })
        });
        
        if (!response.ok) throw new Error("API Request Failed");
        
        const data = await response.json();
        const p_data = data.crisis_params;
        const w_data = data.watchtower;
        const dpi = w_data.dpi_assessment;
        
        badge.className = 'status badge-done';
        badge.innerText = 'COMPLETE';

        // 1. Calculate Colors and Widths
        let riskColor = '#16A34A';
        let riskPulse = '';
        let riskLabel = 'NORMAL';
        if (dpi.probability_30d >= 80) { riskColor = '#DC2626'; riskLabel = 'CRITICAL'; riskPulse = 'animate-pulse'; }
        else if (dpi.probability_30d >= 60) { riskColor = '#EA580C'; riskLabel = 'HIGH'; }
        else if (dpi.probability_30d >= 40) { riskColor = '#CA8A04'; riskLabel = 'ELEVATED'; }
        else if (dpi.probability_30d >= 20) { riskColor = '#2563EB'; riskLabel = 'LOW'; }
        
        // 2. Format HTML Output
        let html = `
            <!-- Agent 1: Watchtower -->
            <div style="background: #111827; border-radius: 12px; padding: 1.5rem; border: 1px solid #374151; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h2 style="color: white; font-size: 1.25rem; font-weight: bold; margin: 0;">⚡ ${dpi.issue.toUpperCase()}</h2>
                    <span class="${riskPulse}" style="background: ${riskColor}; color: white; padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.75rem; font-weight: bold;">
                        ${riskLabel}
                    </span>
                </div>
                
                <div style="position: relative; height: 16px; background: #374151; border-radius: 999px; overflow: hidden; margin-bottom: 0.5rem;">
                    <div style="position: absolute; height: 100%; border-radius: 999px; background: ${riskColor}; width: ${dpi.probability_30d}%; transition: all 1s ease-out;"></div>
                    <div style="position: absolute; top: 0; left: 50%; width: 2px; height: 100%; background: rgba(255,255,255,0.3);"></div>
                </div>
                
                <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #9ca3af; margin-bottom: 1.5rem;">
                    <span>0%</span><span>50%</span><span style="color: white; font-weight: bold;">${dpi.probability_30d}%</span><span>100%</span>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; text-align: center;">
                    <div style="background: #1f2937; border-radius: 8px; padding: 0.75rem;">
                        <div style="font-size: 1.25rem; font-weight: bold; color: white;">${dpi.probability_30d}%</div>
                        <div style="font-size: 0.7rem; color: #9ca3af;">Probability (30d)</div>
                    </div>
                    <div style="background: #1f2937; border-radius: 8px; padding: 0.75rem;">
                        <div style="font-size: 1.25rem; font-weight: bold; color: #4ade80;">${dpi.confidence}%</div>
                        <div style="font-size: 0.7rem; color: #9ca3af;">Confidence</div>
                    </div>
                    <div style="background: #1f2937; border-radius: 8px; padding: 0.75rem;">
                        <div style="font-size: 1.1rem; font-weight: bold; color: #fb923c;">${dpi.trend}</div>
                        <div style="font-size: 0.7rem; color: #9ca3af;">30d Trend</div>
                    </div>
                </div>
            </div>
            
            <h3 style="color: var(--text-main); margin-bottom: 10px; font-size: 0.9rem;">🚨 TRIGGERING EVENTS (${w_data.signals.length})</h3>
            <div style="display: flex; flex-direction: column; gap: 10px; margin-bottom: 20px;">
        `;
        
        if (w_data.signals.length === 0) {
            html += `<div style="padding: 10px; background: #1f2937; border-radius: 8px; color: #9ca3af; font-size: 0.85rem;">Global scan active. No significant signals detected.</div>`;
        } else {
            w_data.signals.forEach(risk => {
                let badgeClass = 'bg-green';
                let sev = parseInt(risk.severity);
                if (sev >= 9) badgeClass = 'bg-red animate-pulse';
                else if (sev >= 7) badgeClass = 'bg-orange';
                else if (sev >= 5) badgeClass = 'bg-yellow';
                else if (sev >= 3) badgeClass = 'bg-blue';
                
                html += `
                    <div class="event-card">
                        <div style="display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 8px;">
                            <b style="color: white; font-size: 0.85rem; display: flex; align-items: center; gap: 8px;">
                                <span class="sev-badge ${badgeClass}">${sev}/10</span>
                                ${risk.event_type.replace('_', ' ').toUpperCase()}
                            </b>
                            <span style="font-size: 0.75rem; color: #6b7280;">${new Date().toLocaleTimeString()}</span>
                        </div>
                        <p style="font-size: 0.85rem; color: #d1d5db; margin-bottom: 8px;">"${risk.description}"</p>
                        <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #9ca3af;">
                            <span>📍 ${risk.impacted_region || p_data.affected_country || 'Global'}</span>
                            <span>🎯 Conf: ${Math.round((risk.confidence || 0.8) * 100)}%</span>
                        </div>
                    </div>
                `;
            });
        }
        
        html += `
            <div style="background: #111827; border-radius: 12px; padding: 1rem; border: 1px solid #374151; margin-top: 15px; display: flex; align-items: center; gap: 15px;">
                <div>
                    <div style="color: white; font-size: 1.5rem; font-weight: bold;">$${w_data.price_anomaly.current_price || '84.50'}</div>
                    <div style="color: #6b7280; font-size: 0.75rem;">Brent Crude</div>
                </div>
                <div style="font-size: 1.1rem; font-weight: bold; color: ${w_data.price_anomaly.is_anomaly ? '#ef4444' : '#4ade80'};">
                    ${w_data.price_anomaly.is_anomaly ? '▲ ANOMALY' : 'NORMAL'}
                </div>
                ${w_data.price_anomaly.is_anomaly ? `
                    <div class="sev-badge bg-red animate-pulse" style="margin-left: auto;">
                        🚨 z-score: ${w_data.price_anomaly.z_score}
                    </div>
                ` : ''}
            </div>
        `;

        if (dpi.probability_30d >= 70) {
            html += `
                <div style="background: rgba(127, 29, 29, 0.3); border: 1px solid #b91c1c; border-radius: 12px; padding: 1rem; margin-top: 20px; animation: pulse 2s infinite;">
                    <div style="color: #f87171; font-weight: bold; font-size: 1.1rem; margin-bottom: 0.5rem;">🚨 THRESHOLD BREACHED (DPI > 70%)</div>
                    <div style="color: white; font-size: 0.9rem; margin-bottom: 0.75rem;">→ Triggering Commander Agent for unified decision...</div>
                </div>
            `;
        } else {
            html += `
                <div style="background: rgba(20, 83, 45, 0.3); border: 1px solid #15803d; border-radius: 12px; padding: 1rem; margin-top: 20px;">
                    <div style="color: #4ade80; font-weight: bold; margin-bottom: 0.25rem;">✅ Risk Below Action Threshold</div>
                    <div style="color: #9ca3af; font-size: 0.85rem;">Continuing monitoring... Next scan in 15 minutes.</div>
                </div>
            `;
        }

        body.innerHTML = html;

    } catch (err) {
        console.error(err);
        badge.className = 'status badge-pending';
        badge.innerText = 'ERROR';
        body.innerHTML = '<p class="critical">Failed to run the Watchtower agent. Check the backend console.</p>';
    } finally {
        btn.disabled = false;
        btn.innerText = "Analyze Global Risk";
    }
});
