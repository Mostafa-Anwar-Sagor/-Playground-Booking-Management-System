// Enhanced TypeScript for dynamic partner applications admin dashboard
// Professional, modern, robust, and accessible
document.addEventListener('DOMContentLoaded', () => {
    const appDataArr = JSON.parse(document.getElementById('partner-applications-json').textContent || '[]');
    const appData = {};
    appDataArr.forEach((app) => { appData[String(app.id)] = app; });
    window._partnerAppData = appData;

    // Initialize stats
    updateStats();
    
    // Enhanced modal display with better design and features
    function showPartnerAppDetailsModal(appId) {
        const modal = document.getElementById('partnerAppDetailsModal');
        const body = document.getElementById('partnerAppDetailsBody');
        body.innerHTML = '';
        
        const app = appData[String(appId)];
        if (!app) {
            body.innerHTML = '<div style="color:#ef4444;font-weight:700;text-align:center;padding:2rem;"><i class="fas fa-exclamation-triangle" style="font-size:2rem;margin-bottom:1rem;display:block;"></i>No data found for this application.</div>';
            modal.style.display = 'flex';
            return;
        }

        // Create comprehensive application details
        let html = `
            <div style="position:relative;">
                <div style="text-align:center;margin-bottom:2rem;">
                    <div style="display:flex;align-items:center;justify-content:center;gap:1rem;margin-bottom:1rem;">
                        <div style="width:60px;height:60px;background:linear-gradient(135deg,#10b981 0%,#3b82f6 100%);border-radius:50%;display:flex;align-items:center;justify-content:center;">
                            <i class="fas fa-user-tie" style="font-size:1.5rem;color:white;"></i>
                        </div>
                        <div style="text-align:left;">
                            <h2 style="font-size:2rem;font-weight:900;background:linear-gradient(90deg,#10b981 0%,#3b82f6 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:0;">${app.business || 'Business Application'}</h2>
                            <div style="font-size:1rem;color:#94a3b8;">Application #${app.id} • Submitted ${app.created}</div>
                        </div>
                    </div>
                </div>
        `;

        // Status-specific action buttons
        if (app.status === 'pending') {
            html += `
                <div style="position:sticky;top:0;z-index:10;display:flex;justify-content:center;gap:1.5rem;margin-bottom:2rem;padding:1.5rem;background:rgba(30,41,59,0.95);border-radius:1rem;backdrop-filter:blur(10px);border:1px solid rgba(59,130,246,0.3);">
                    <button class='admin-button success' style='min-width:160px;padding:1rem 1.5rem;font-size:1.1rem;' onclick="handlePartnerAppAction('${app.id}','approve',this)">
                        <i class="fas fa-check-circle"></i> Approve Application
                    </button>
                    <button class='admin-button danger' style='min-width:160px;padding:1rem 1.5rem;font-size:1.1rem;' onclick="handlePartnerAppAction('${app.id}','reject',this)">
                        <i class="fas fa-times-circle"></i> Reject Application
                    </button>
                </div>
            `;
        } else {
            const statusColor = app.status === 'approved' ? '#10b981' : '#ef4444';
            const statusIcon = app.status === 'approved' ? 'check-circle' : 'times-circle';
            const statusBg = app.status === 'approved' ? '16,185,129' : '239,68,68';
            html += `
                <div style="text-align:center;margin-bottom:2rem;padding:1.5rem;background:rgba(${statusBg},0.1);border:2px solid rgba(${statusBg},0.3);border-radius:1rem;">
                    <i class="fas fa-${statusIcon}" style="font-size:3rem;color:${statusColor};margin-bottom:1rem;"></i>
                    <div style="font-size:1.4rem;font-weight:700;color:${statusColor};margin-bottom:0.5rem;">Application ${app.status.charAt(0).toUpperCase() + app.status.slice(1)}</div>
                    ${app.approved_by ? `<div style="color:#94a3b8;font-size:0.9rem;">by ${app.approved_by}</div>` : ''}
                    ${app.updated ? `<div style="color:#94a3b8;font-size:0.9rem;">on ${app.updated}</div>` : ''}
                </div>
            `;
        }

        // Application Overview Summary
        html += `
            <div style="margin-bottom:2rem;padding:1.5rem;background:linear-gradient(135deg,rgba(59,130,246,0.1),rgba(16,185,129,0.1));border:1px solid rgba(59,130,246,0.3);border-radius:1rem;">
                <h3 style="color:#3b82f6;font-size:1.3rem;font-weight:700;margin-bottom:1rem;display:flex;align-items:center;gap:0.5rem;">
                    <i class="fas fa-clipboard-list"></i> Application Summary
                </h3>
                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem;">
                    <div style="text-align:center;padding:1rem;background:rgba(15,23,42,0.6);border-radius:0.75rem;">
                        <div style="font-size:1.5rem;font-weight:700;color:#10b981;">${app.experience_years || 0}</div>
                        <div style="color:#94a3b8;font-size:0.9rem;">Years Experience</div>
                    </div>
                    <div style="text-align:center;padding:1rem;background:rgba(15,23,42,0.6);border-radius:0.75rem;">
                        <div style="font-size:1.5rem;font-weight:700;color:#3b82f6;">${app.images_count || 0}</div>
                        <div style="color:#94a3b8;font-size:0.9rem;">Images Uploaded</div>
                    </div>
                    <div style="text-align:center;padding:1rem;background:rgba(15,23,42,0.6);border-radius:0.75rem;">
                        <div style="font-size:1.5rem;font-weight:700;color:#8b5cf6;">${app.videos_count || 0}</div>
                        <div style="color:#94a3b8;font-size:0.9rem;">Videos Uploaded</div>
                    </div>
                    <div style="text-align:center;padding:1rem;background:rgba(15,23,42,0.6);border-radius:0.75rem;">
                        <div style="font-size:1.5rem;font-weight:700;color:#${app.business_license ? '10b981' : 'ef4444'};">
                            <i class="fas fa-${app.business_license ? 'check' : 'times'}"></i>
                        </div>
                        <div style="color:#94a3b8;font-size:0.9rem;">License ${app.business_license ? 'Provided' : 'Missing'}</div>
                    </div>
                </div>
            </div>
        `;

        // Owner Information Section
        html += `
            <div style="margin-bottom:2rem;">
                <h3 style="color:#3b82f6;font-size:1.5rem;font-weight:700;margin-bottom:1rem;display:flex;align-items:center;gap:0.5rem;">
                    <i class="fas fa-user-circle"></i> Owner Information
                </h3>
                <div style="background:rgba(15,23,42,0.5);padding:2rem;border-radius:1rem;border:1px solid rgba(59,130,246,0.2);">
                    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1.5rem;">
                        <div style="display:flex;align-items:center;gap:1rem;padding:1rem;background:rgba(59,130,246,0.1);border-radius:0.75rem;border:1px solid rgba(59,130,246,0.2);">
                            <div style="width:40px;height:40px;background:#3b82f6;border-radius:50%;display:flex;align-items:center;justify-content:center;">
                                <i class="fas fa-user" style="color:white;"></i>
                            </div>
                            <div>
                                <div style="color:#60a5fa;font-size:0.9rem;font-weight:600;">Full Name</div>
                                <div style="color:#e5e7eb;font-size:1.1rem;font-weight:600;">${app.owner || 'Not provided'}</div>
                            </div>
                        </div>
                        <div style="display:flex;align-items:center;gap:1rem;padding:1rem;background:rgba(59,130,246,0.1);border-radius:0.75rem;border:1px solid rgba(59,130,246,0.2);">
                            <div style="width:40px;height:40px;background:#3b82f6;border-radius:50%;display:flex;align-items:center;justify-content:center;">
                                <i class="fas fa-envelope" style="color:white;"></i>
                            </div>
                            <div>
                                <div style="color:#60a5fa;font-size:0.9rem;font-weight:600;">Email Address</div>
                                <div style="color:#e5e7eb;font-size:1.1rem;font-weight:600;">${app.owner_email || 'Not provided'}</div>
                            </div>
                        </div>
                        <div style="display:flex;align-items:center;gap:1rem;padding:1rem;background:rgba(59,130,246,0.1);border-radius:0.75rem;border:1px solid rgba(59,130,246,0.2);">
                            <div style="width:40px;height:40px;background:#3b82f6;border-radius:50%;display:flex;align-items:center;justify-content:center;">
                                <i class="fas fa-phone" style="color:white;"></i>
                            </div>
                            <div>
                                <div style="color:#60a5fa;font-size:0.9rem;font-weight:600;">Phone Number</div>
                                <div style="color:#e5e7eb;font-size:1.1rem;font-weight:600;">${app.owner_phone || 'Not provided'}</div>
                            </div>
                        </div>
                        <div style="display:flex;align-items:center;gap:1rem;padding:1rem;background:rgba(59,130,246,0.1);border-radius:0.75rem;border:1px solid rgba(59,130,246,0.2);">
                            <div style="width:40px;height:40px;background:#3b82f6;border-radius:50%;display:flex;align-items:center;justify-content:center;">
                                <i class="fas fa-map-marker-alt" style="color:white;"></i>
                            </div>
                            <div>
                                <div style="color:#60a5fa;font-size:0.9rem;font-weight:600;">Address</div>
                                <div style="color:#e5e7eb;font-size:1.1rem;font-weight:600;">${app.owner_address || 'Not provided'}</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Business Information Section
        html += `
            <div style="margin-bottom:2rem;">
                <h3 style="color:#10b981;font-size:1.5rem;font-weight:700;margin-bottom:1rem;display:flex;align-items:center;gap:0.5rem;">
                    <i class="fas fa-building"></i> Business Information
                </h3>
                <div style="background:rgba(15,23,42,0.5);padding:2rem;border-radius:1rem;border:1px solid rgba(16,185,129,0.2);">
                    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1.5rem;">
                        <div style="display:flex;align-items:center;gap:1rem;padding:1rem;background:rgba(16,185,129,0.1);border-radius:0.75rem;border:1px solid rgba(16,185,129,0.2);">
                            <div style="width:40px;height:40px;background:#10b981;border-radius:50%;display:flex;align-items:center;justify-content:center;">
                                <i class="fas fa-store" style="color:white;"></i>
                            </div>
                            <div>
                                <div style="color:#10b981;font-size:0.9rem;font-weight:600;">Business Name</div>
                                <div style="color:#e5e7eb;font-size:1.1rem;font-weight:600;">${app.business || 'Not provided'}</div>
                            </div>
                        </div>
                        <div style="display:flex;align-items:center;gap:1rem;padding:1rem;background:rgba(16,185,129,0.1);border-radius:0.75rem;border:1px solid rgba(16,185,129,0.2);">
                            <div style="width:40px;height:40px;background:#10b981;border-radius:50%;display:flex;align-items:center;justify-content:center;">
                                <i class="fas fa-envelope" style="color:white;"></i>
                            </div>
                            <div>
                                <div style="color:#10b981;font-size:0.9rem;font-weight:600;">Business Email</div>
                                <div style="color:#e5e7eb;font-size:1.1rem;font-weight:600;">${app.email || 'Not provided'}</div>
                            </div>
                        </div>
                        <div style="display:flex;align-items:center;gap:1rem;padding:1rem;background:rgba(16,185,129,0.1);border-radius:0.75rem;border:1px solid rgba(16,185,129,0.2);">
                            <div style="width:40px;height:40px;background:#10b981;border-radius:50%;display:flex;align-items:center;justify-content:center;">
                                <i class="fas fa-phone" style="color:white;"></i>
                            </div>
                            <div>
                                <div style="color:#10b981;font-size:0.9rem;font-weight:600;">Business Phone</div>
                                <div style="color:#e5e7eb;font-size:1.1rem;font-weight:600;">${app.phone || 'Not provided'}</div>
                            </div>
                        </div>
                        <div style="display:flex;align-items:center;gap:1rem;padding:1rem;background:rgba(16,185,129,0.1);border-radius:0.75rem;border:1px solid rgba(16,185,129,0.2);">
                            <div style="width:40px;height:40px;background:#10b981;border-radius:50%;display:flex;align-items:center;justify-content:center;">
                                <i class="fas fa-clock" style="color:white;"></i>
                            </div>
                            <div>
                                <div style="color:#10b981;font-size:0.9rem;font-weight:600;">Experience</div>
                                <div style="color:#e5e7eb;font-size:1.1rem;font-weight:600;">${app.experience_years || 0} years</div>
                            </div>
                        </div>
                    </div>
                    <div style="margin-top:1.5rem;padding:1rem;background:rgba(16,185,129,0.1);border-radius:0.75rem;border:1px solid rgba(16,185,129,0.2);">
                        <div style="color:#10b981;font-size:0.9rem;font-weight:600;margin-bottom:0.5rem;">Business Address</div>
                        <div style="color:#e5e7eb;font-size:1.1rem;line-height:1.5;">${app.address || 'Not provided'}</div>
                    </div>
                </div>
            </div>
        `;

        // Description Section
        if (app.description && app.description.trim()) {
            html += `
                <div style="margin-bottom:2rem;">
                    <h3 style="color:#f59e0b;font-size:1.5rem;font-weight:700;margin-bottom:1rem;display:flex;align-items:center;gap:0.5rem;">
                        <i class="fas fa-file-alt"></i> Business Description
                    </h3>
                    <div style="background:rgba(15,23,42,0.5);padding:2rem;border-radius:1rem;border:1px solid rgba(245,158,11,0.2);color:#e5e7eb;line-height:1.8;font-size:1.1rem;">
                        ${app.description.replace(/\n/g, '<br>')}
                    </div>
                </div>
            `;
        } else {
            html += `
                <div style="margin-bottom:2rem;">
                    <h3 style="color:#f59e0b;font-size:1.5rem;font-weight:700;margin-bottom:1rem;display:flex;align-items:center;gap:0.5rem;">
                        <i class="fas fa-file-alt"></i> Business Description
                    </h3>
                    <div style="background:rgba(15,23,42,0.5);padding:2rem;border-radius:1rem;border:1px solid rgba(245,158,11,0.2);text-align:center;color:#64748b;">
                        <i class="fas fa-info-circle" style="font-size:2rem;margin-bottom:1rem;display:block;"></i>
                        No business description provided
                    </div>
                </div>
            `;
        }

        // Admin Comments Section
        html += `
            <div style="margin-bottom:2rem;">
                <h3 style="color:#8b5cf6;font-size:1.5rem;font-weight:700;margin-bottom:1rem;display:flex;align-items:center;gap:0.5rem;">
                    <i class="fas fa-comment-alt"></i> Admin Comments & Notes
                </h3>
                <div style="background:rgba(15,23,42,0.5);padding:2rem;border-radius:1rem;border:1px solid rgba(139,92,246,0.2);min-height:80px;">
                    ${app.admin_comments && app.admin_comments.trim() ? 
                        `<div style="color:#e5e7eb;line-height:1.6;font-size:1.1rem;margin-bottom:1rem;">${app.admin_comments.replace(/\n/g, '<br>')}</div>` : 
                        `<div style="color:#64748b;font-style:italic;text-align:center;padding:1rem;">
                            <i class="fas fa-comment-slash" style="font-size:2rem;margin-bottom:1rem;display:block;"></i>
                            No admin comments yet
                        </div>`
                    }
                    <div style="text-align:center;margin-top:1rem;">
                        <button class="admin-button secondary" onclick="openCommentModal('${app.id}', '${(app.admin_comments || '').replace(/'/g, "\\'")}')">
                            <i class="fas fa-edit"></i> ${app.admin_comments && app.admin_comments.trim() ? 'Edit Comments' : 'Add Comments'}
                        </button>
                    </div>
                </div>
            </div>
        `;

        // Business License Section
        html += `
            <div style="margin-bottom:2rem;">
                <h3 style="color:#ef4444;font-size:1.5rem;font-weight:700;margin-bottom:1rem;display:flex;align-items:center;gap:0.5rem;">
                    <i class="fas fa-certificate"></i> Business License Document
                </h3>
        `;
        
        if (app.business_license && app.business_license.trim()) {
            html += `
                <div style="text-align:center;background:rgba(15,23,42,0.5);padding:2rem;border-radius:1rem;border:1px solid rgba(239,68,68,0.2);">
                    <div style="margin-bottom:1rem;">
                        <i class="fas fa-file-image" style="font-size:2rem;color:#10b981;margin-bottom:0.5rem;"></i>
                        <div style="color:#10b981;font-weight:600;margin-bottom:1rem;">License Document Available</div>
                    </div>
                    <div style="max-width:500px;margin:0 auto;position:relative;border-radius:1rem;overflow:hidden;box-shadow:0 10px 30px rgba(0,0,0,0.4);">
                        <img src='${app.business_license}' style='width:100%;max-height:400px;object-fit:contain;cursor:pointer;transition:transform 0.2s;' onclick="window.open('${app.business_license}', '_blank')" onmouseover="this.style.transform='scale(1.02)'" onmouseout="this.style.transform='scale(1)'" title="Click to view full size" />
                        <div style="position:absolute;top:1rem;right:1rem;background:rgba(0,0,0,0.7);color:white;padding:0.5rem 1rem;border-radius:0.5rem;font-size:0.9rem;">
                            <i class="fas fa-expand"></i> Click to enlarge
                        </div>
                    </div>
                    <div style="margin-top:1rem;">
                        <button onclick="window.open('${app.business_license}', '_blank')" style="background:linear-gradient(135deg,#10b981 0%,#3b82f6 100%);color:white;border:none;padding:0.75rem 1.5rem;border-radius:0.75rem;font-weight:600;cursor:pointer;transition:all 0.2s;" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
                            <i class="fas fa-external-link-alt"></i> View Full Size
                        </button>
                    </div>
                </div>
            `;
        } else {
            html += `
                <div style="text-align:center;background:rgba(15,23,42,0.5);padding:2rem;border-radius:1rem;border:1px solid rgba(239,68,68,0.2);color:#64748b;">
                    <i class="fas fa-exclamation-triangle" style="font-size:3rem;color:#ef4444;margin-bottom:1rem;"></i>
                    <div style="font-size:1.2rem;font-weight:600;color:#ef4444;margin-bottom:0.5rem;">No Business License Uploaded</div>
                    <div style="font-size:0.9rem;">The applicant has not provided a business license document</div>
                </div>
            `;
        }
        html += `</div>`;

        // Images Section
        html += `
            <div style="margin-bottom:2rem;">
                <h3 style="color:#06b6d4;font-size:1.5rem;font-weight:700;margin-bottom:1rem;display:flex;align-items:center;gap:0.5rem;">
                    <i class="fas fa-images"></i> Business Images Gallery
                    <span style="background:rgba(6,182,212,0.2);color:#06b6d4;padding:0.3rem 0.8rem;border-radius:1rem;font-size:0.9rem;">${app.images ? app.images.length : 0} images</span>
                </h3>
        `;
        
        if (app.images && app.images.length > 0) {
            html += `
                <div style="background:rgba(15,23,42,0.5);padding:2rem;border-radius:1rem;border:1px solid rgba(6,182,212,0.2);">
                    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:1.5rem;">
            `;
            app.images.forEach((url, index) => {
                if (url && url.trim()) {
                    html += `
                        <div style="position:relative;border-radius:1rem;overflow:hidden;box-shadow:0 8px 25px rgba(0,0,0,0.3);transition:all 0.3s;background:#1e293b;" onmouseover="this.style.transform='translateY(-8px) scale(1.02)';this.style.boxShadow='0 15px 35px rgba(6,182,212,0.3)'" onmouseout="this.style.transform='translateY(0) scale(1)';this.style.boxShadow='0 8px 25px rgba(0,0,0,0.3)'">
                            <img src='${url}' style='width:100%;height:200px;object-fit:cover;cursor:pointer;transition:all 0.2s;' onclick="window.open('${url}', '_blank')" title="Click to view full size" />
                            <div style="position:absolute;top:0.5rem;left:0.5rem;background:rgba(6,182,212,0.9);color:white;padding:0.3rem 0.8rem;border-radius:0.5rem;font-size:0.8rem;font-weight:600;">
                                Image ${index + 1}
                            </div>
                            <div style="position:absolute;bottom:0;left:0;right:0;background:linear-gradient(transparent,rgba(0,0,0,0.8));color:white;padding:1rem 0.5rem 0.5rem;text-align:center;">
                                <i class="fas fa-search-plus"></i> Click to enlarge
                            </div>
                        </div>
                    `;
                }
            });
            html += `
                    </div>
                    <div style="text-align:center;margin-top:1.5rem;color:#94a3b8;font-size:0.9rem;">
                        <i class="fas fa-info-circle"></i> Click on any image to view it in full size
                    </div>
                </div>
            `;
        } else {
            html += `
                <div style="text-align:center;background:rgba(15,23,42,0.5);padding:2rem;border-radius:1rem;border:1px solid rgba(6,182,212,0.2);color:#64748b;">
                    <i class="fas fa-camera" style="font-size:3rem;color:#06b6d4;margin-bottom:1rem;"></i>
                    <div style="font-size:1.2rem;font-weight:600;color:#06b6d4;margin-bottom:0.5rem;">No Business Images</div>
                    <div style="font-size:0.9rem;">The applicant has not uploaded any business images</div>
                </div>
            `;
        }
        html += `</div>`;

        // Videos Section
        html += `
            <div style="margin-bottom:2rem;">
                <h3 style="color:#a855f7;font-size:1.5rem;font-weight:700;margin-bottom:1rem;display:flex;align-items:center;gap:0.5rem;">
                    <i class="fas fa-video"></i> Business Videos Showcase
                    <span style="background:rgba(168,85,247,0.2);color:#a855f7;padding:0.3rem 0.8rem;border-radius:1rem;font-size:0.9rem;">${app.videos ? app.videos.length : 0} videos</span>
                </h3>
        `;
        
        if (app.videos && app.videos.length > 0) {
            html += `
                <div style="background:rgba(15,23,42,0.5);padding:2rem;border-radius:1rem;border:1px solid rgba(168,85,247,0.2);">
                    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(350px,1fr));gap:1.5rem;">
            `;
            app.videos.forEach((url, index) => {
                if (url && url.trim()) {
                    html += `
                        <div style="position:relative;border-radius:1rem;overflow:hidden;box-shadow:0 8px 25px rgba(0,0,0,0.3);transition:all 0.3s;background:#1e293b;" onmouseover="this.style.transform='translateY(-8px)';this.style.boxShadow='0 15px 35px rgba(168,85,247,0.3)'" onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='0 8px 25px rgba(0,0,0,0.3)'">
                            <video src='${url}' controls style='width:100%;height:250px;object-fit:cover;' preload="metadata" controlsList="nodownload">
                                Your browser does not support the video tag.
                            </video>
                            <div style="position:absolute;top:0.5rem;left:0.5rem;background:rgba(168,85,247,0.9);color:white;padding:0.3rem 0.8rem;border-radius:0.5rem;font-size:0.8rem;font-weight:600;">
                                Video ${index + 1}
                            </div>
                        </div>
                    `;
                }
            });
            html += `
                    </div>
                    <div style="text-align:center;margin-top:1.5rem;color:#94a3b8;font-size:0.9rem;">
                        <i class="fas fa-play-circle"></i> Use video controls to play, pause, and adjust volume
                    </div>
                </div>
            `;
        } else {
            html += `
                <div style="text-align:center;background:rgba(15,23,42,0.5);padding:2rem;border-radius:1rem;border:1px solid rgba(168,85,247,0.2);color:#64748b;">
                    <i class="fas fa-video-slash" style="font-size:3rem;color:#a855f7;margin-bottom:1rem;"></i>
                    <div style="font-size:1.2rem;font-weight:600;color:#a855f7;margin-bottom:0.5rem;">No Business Videos</div>
                    <div style="font-size:0.9rem;">The applicant has not uploaded any business videos</div>
                </div>
            `;
        }
        html += `</div>`;

        // Application Timeline
        html += `
            <div style="margin-bottom:2rem;">
                <h3 style="color:#64748b;font-size:1.5rem;font-weight:700;margin-bottom:1rem;display:flex;align-items:center;gap:0.5rem;">
                    <i class="fas fa-timeline"></i> Application Timeline
                </h3>
                <div style="background:rgba(15,23,42,0.5);padding:2rem;border-radius:1rem;border:1px solid rgba(100,116,139,0.2);">
                    <div style="display:flex;flex-direction:column;gap:1rem;">
                        <div style="display:flex;align-items:center;gap:1rem;padding:1rem;background:rgba(59,130,246,0.1);border-radius:0.75rem;border-left:4px solid #3b82f6;">
                            <i class="fas fa-plus-circle" style="color:#3b82f6;font-size:1.2rem;"></i>
                            <div>
                                <div style="color:#e5e7eb;font-weight:600;">Application Submitted</div>
                                <div style="color:#94a3b8;font-size:0.9rem;">${app.created}</div>
                            </div>
                        </div>
                        ${app.status !== 'pending' ? `
                            <div style="display:flex;align-items:center;gap:1rem;padding:1rem;background:rgba(${app.status === 'approved' ? '16,185,129' : '239,68,68'},0.1);border-radius:0.75rem;border-left:4px solid ${app.status === 'approved' ? '#10b981' : '#ef4444'};">
                                <i class="fas fa-${app.status === 'approved' ? 'check-circle' : 'times-circle'}" style="color:${app.status === 'approved' ? '#10b981' : '#ef4444'};font-size:1.2rem;"></i>
                                <div>
                                    <div style="color:#e5e7eb;font-weight:600;">Application ${app.status === 'approved' ? 'Approved' : 'Rejected'}</div>
                                    <div style="color:#94a3b8;font-size:0.9rem;">${app.updated}${app.approved_by ? ` by ${app.approved_by}` : ''}</div>
                                </div>
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;

        html += `</div>`;

        body.innerHTML = html;
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden'; // Prevent background scrolling
    }

    window.showPartnerAppDetailsModal = showPartnerAppDetailsModal;
    // Attach click listeners to table rows
    document.querySelectorAll('.partner-app-row').forEach(row => {
        // Add visual feedback for clickable rows
        row.style.cursor = 'pointer';
        
        row.addEventListener('click', (e) => {
            if (e.target.closest('.app-action-btn') || e.target.closest('input[type="checkbox"]')) return;
            const appId = String(row.getAttribute('data-app-id'));
            showPartnerAppDetailsModal(appId);
        });
        
        row.addEventListener('keydown', (e) => {
            if ((e.key === 'Enter' || e.key === ' ') && !e.target.closest('.app-action-btn')) {
                e.preventDefault();
                const appId = String(row.getAttribute('data-app-id'));
                showPartnerAppDetailsModal(appId);
            }
        });

        // Add hover tooltip for better UX
        row.addEventListener('mouseenter', () => {
            if (!row.dataset.tooltipAdded) {
                row.dataset.tooltipAdded = 'true';
                const tooltip = document.createElement('div');
                tooltip.style.cssText = `
                    position: absolute;
                    top: -35px;
                    left: 50%;
                    transform: translateX(-50%);
                    background: rgba(59,130,246,0.9);
                    color: white;
                    padding: 0.5rem 1rem;
                    border-radius: 0.5rem;
                    font-size: 0.8rem;
                    font-weight: 600;
                    white-space: nowrap;
                    z-index: 1000;
                    pointer-events: none;
                    opacity: 0;
                    transition: opacity 0.2s;
                `;
                tooltip.textContent = 'Click to view full application details';
                row.style.position = 'relative';
                row.appendChild(tooltip);
                
                setTimeout(() => {
                    tooltip.style.opacity = '1';
                }, 100);
                
                setTimeout(() => {
                    if (tooltip.parentNode) {
                        tooltip.style.opacity = '0';
                        setTimeout(() => {
                            if (tooltip.parentNode) tooltip.remove();
                        }, 200);
                    }
                }, 2000);
            }
        });
    });

    // Modal close functions
    window.closePartnerAppDetailsModal = function () {
        document.getElementById('partnerAppDetailsModal').style.display = 'none';
        document.body.style.overflow = 'auto';
    };

    window.closeCommentModal = function () {
        document.getElementById('commentModal').style.display = 'none';
        document.body.style.overflow = 'auto';
    };

    // Statistics update function
    function updateStats() {
        const apps = Object.values(appData);
        const pending = apps.filter(app => app.status === 'pending').length;
        const approved = apps.filter(app => app.status === 'approved').length;
        const rejected = apps.filter(app => app.status === 'rejected').length;
        const total = apps.length;

        document.getElementById('pendingCount').textContent = pending;
        document.getElementById('approvedCount').textContent = approved;
        document.getElementById('rejectedCount').textContent = rejected;
        document.getElementById('totalCount').textContent = total;
    }

    window.updateStats = updateStats;
});

// Comment Modal Functions
window.openCommentModal = function(appId, currentComments) {
    const modal = document.getElementById('commentModal');
    const textarea = document.getElementById('adminComments');
    
    // Store current app ID for saving
    modal.dataset.appId = appId;
    textarea.value = currentComments || '';
    
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
    
    // Focus on textarea
    setTimeout(() => textarea.focus(), 100);
};

window.saveComments = function() {
    const modal = document.getElementById('commentModal');
    const textarea = document.getElementById('adminComments');
    const appId = modal.dataset.appId;
    const comments = textarea.value.trim();

    if (!appId) return;

    // Show loading state
    const saveBtn = event.target;
    const originalText = saveBtn.innerHTML;
    saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
    saveBtn.disabled = true;

    fetch(window.location.pathname, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value || '',
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `application_id=${appId}&action=update_comments&comments=${encodeURIComponent(comments)}`
    })
    .then(res => res.json())
    .then(data => {
        showNotification(data.message, data.success ? 'success' : 'error');
        
        if (data.success) {
            // Update local data
            if (window._partnerAppData[appId]) {
                window._partnerAppData[appId].admin_comments = comments;
            }
            
            window.closeCommentModal();
            
            // If detail modal is open, refresh it
            const detailModal = document.getElementById('partnerAppDetailsModal');
            if (detailModal.style.display === 'flex') {
                showPartnerAppDetailsModal(appId);
            }
            
            // Update table if needed
            setTimeout(() => window.location.reload(), 1000);
        } else {
            saveBtn.innerHTML = originalText;
            saveBtn.disabled = false;
        }
    })
    .catch(() => {
        showNotification('Error saving comments. Please try again.', 'error');
        saveBtn.innerHTML = originalText;
        saveBtn.disabled = false;
    });
};

// Filter and Search Functions
window.filterApplications = function(status) {
    const rows = document.querySelectorAll('.partner-app-row');
    const buttons = document.querySelectorAll('.filter-button');
    
    // Update active button
    buttons.forEach(btn => btn.classList.remove('active'));
    document.querySelector(`[data-filter="${status}"]`).classList.add('active');
    
    // Filter rows
    rows.forEach(row => {
        const rowStatus = row.dataset.status;
        if (status === 'all' || rowStatus === status) {
            row.style.display = '';
            row.classList.add('fade-in');
        } else {
            row.style.display = 'none';
            row.classList.remove('fade-in');
        }
    });
    
    // Update visible count
    updateVisibleCount();
};

window.searchApplications = function() {
    const query = document.getElementById('searchInput').value.toLowerCase();
    const rows = document.querySelectorAll('.partner-app-row');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        if (text.includes(query)) {
            row.style.display = '';
            row.classList.add('fade-in');
        } else {
            row.style.display = 'none';
            row.classList.remove('fade-in');
        }
    });
    
    updateVisibleCount();
};

function updateVisibleCount() {
    const visibleRows = document.querySelectorAll('.partner-app-row[style=""], .partner-app-row:not([style])').length;
    // Could add a count display here if needed
}

// Bulk Actions
window.toggleSelectAll = function() {
    const selectAll = document.getElementById('selectAll');
    const checkboxes = document.querySelectorAll('.app-checkbox');
    
    checkboxes.forEach(checkbox => {
        checkbox.checked = selectAll.checked;
    });
    
    updateBulkActions();
};

window.updateBulkActions = function() {
    const checkboxes = document.querySelectorAll('.app-checkbox:checked');
    const container = document.getElementById('bulkActionsContainer');
    const count = document.getElementById('selectedCount');
    
    count.textContent = checkboxes.length;
    container.style.display = checkboxes.length > 0 ? 'block' : 'none';
    
    // Enable/disable bulk action buttons based on status
    const selectedIds = Array.from(checkboxes).map(cb => cb.value);
    const pendingSelected = selectedIds.filter(id => 
        window._partnerAppData[id] && window._partnerAppData[id].status === 'pending'
    ).length;
    
    document.getElementById('bulkApproveBtn').disabled = pendingSelected === 0;
    document.getElementById('bulkRejectBtn').disabled = pendingSelected === 0;
};

window.bulkApprove = function() {
    const checkboxes = document.querySelectorAll('.app-checkbox:checked');
    const selectedIds = Array.from(checkboxes)
        .map(cb => cb.value)
        .filter(id => window._partnerAppData[id] && window._partnerAppData[id].status === 'pending');
    
    if (selectedIds.length === 0) {
        showNotification('No pending applications selected.', 'error');
        return;
    }
    
    if (!confirm(`Are you sure you want to approve ${selectedIds.length} application(s)?`)) return;
    
    bulkAction(selectedIds, 'approve');
};

window.bulkReject = function() {
    const checkboxes = document.querySelectorAll('.app-checkbox:checked');
    const selectedIds = Array.from(checkboxes)
        .map(cb => cb.value)
        .filter(id => window._partnerAppData[id] && window._partnerAppData[id].status === 'pending');
    
    if (selectedIds.length === 0) {
        showNotification('No pending applications selected.', 'error');
        return;
    }
    
    if (!confirm(`Are you sure you want to reject ${selectedIds.length} application(s)?`)) return;
    
    bulkAction(selectedIds, 'reject');
};

function bulkAction(ids, action) {
    const container = document.getElementById('bulkActionsContainer');
    container.classList.add('loading');
    
    Promise.all(ids.map(id => 
        fetch(window.location.pathname, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value || '',
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `application_id=${id}&action=${action}`
        }).then(res => res.json())
    ))
    .then(responses => {
        const successful = responses.filter(r => r.success).length;
        const failed = responses.length - successful;
        
        if (successful > 0) {
            showNotification(`Successfully ${action}ed ${successful} application(s).`, 'success');
        }
        if (failed > 0) {
            showNotification(`Failed to ${action} ${failed} application(s).`, 'error');
        }
        
        setTimeout(() => window.location.reload(), 1000);
    })
    .catch(() => {
        showNotification('Error processing bulk action. Please try again.', 'error');
        container.classList.remove('loading');
    });
}

window.clearSelection = function() {
    document.querySelectorAll('.app-checkbox').forEach(cb => cb.checked = false);
    document.getElementById('selectAll').checked = false;
    updateBulkActions();
};

// Utility Functions
window.exportApplications = function() {
    const data = Object.values(window._partnerAppData);
    const csv = convertToCSV(data);
    downloadCSV(csv, 'partner_applications.csv');
};

function convertToCSV(data) {
    const headers = ['ID', 'Owner', 'Business', 'Email', 'Status', 'Experience', 'Submitted'];
    const rows = data.map(app => [
        app.id,
        app.owner,
        app.business,
        app.email,
        app.status,
        `${app.experience_years || 0} years`,
        app.created
    ]);
    
    return [headers, ...rows]
        .map(row => row.map(field => `"${(field || '').toString().replace(/"/g, '""')}"`).join(','))
        .join('\n');
}

function downloadCSV(csv, filename) {
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

window.refreshData = function() {
    const btn = event.target;
    const originalHTML = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Refreshing...';
    btn.disabled = true;
    
    setTimeout(() => {
        window.location.reload();
    }, 500);
};

function showNotification(message, type = 'success') {
    // Remove existing notifications
    document.querySelectorAll('.notification').forEach(n => n.remove());
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div style="display:flex;align-items:center;gap:0.5rem;">
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'}"></i>
            ${message}
        </div>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Enhanced Action handler with improved error handling and UX
function handlePartnerAppAction(appId, action, btn) {
    if (!confirm(`Are you sure you want to ${action} this application?`)) return;
    
    const originalHTML = btn.innerHTML;
    btn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> ${action === 'approve' ? 'Approving' : 'Rejecting'}...`;
    btn.disabled = true;
    
    fetch(window.location.pathname, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value || '',
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `application_id=${appId}&action=${action}`
    })
    .then(res => res.json())
    .then(data => {
        showNotification(data.message, data.success ? 'success' : 'error');
        
        if (data.success) {
            // Update local data
            if (window._partnerAppData[appId]) {
                window._partnerAppData[appId].status = action === 'approve' ? 'approved' : 'rejected';
            }
            
            // Close any open modals
            window.closePartnerAppDetailsModal();
            
            setTimeout(() => window.location.reload(), 1200);
        } else {
            btn.innerHTML = originalHTML;
            btn.disabled = false;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error processing request. Please try again.', 'error');
        btn.innerHTML = originalHTML;
        btn.disabled = false;
    });
}

window.handlePartnerAppAction = handlePartnerAppAction;

// Close modals when clicking outside
document.addEventListener('click', (e) => {
    const detailModal = document.getElementById('partnerAppDetailsModal');
    const commentModal = document.getElementById('commentModal');
    
    if (e.target === detailModal) {
        window.closePartnerAppDetailsModal();
    }
    if (e.target === commentModal) {
        window.closeCommentModal();
    }
});

// Keyboard navigation
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        window.closePartnerAppDetailsModal();
        window.closeCommentModal();
    }
});

export {};
