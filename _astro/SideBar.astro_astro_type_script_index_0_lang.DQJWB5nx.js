import{w as l}from"./widget-manager.C8kMla_W.js";import"./config.CHaB2CpH.js";class h{constructor(){this.init(),this.initOutlineVisibility()}init(){this.updateResponsiveDisplay(),window.addEventListener("resize",()=>this.updateResponsiveDisplay())}updateResponsiveDisplay(){const e=l.getBreakpoints(),s=window.innerWidth;let i;s<e.mobile?i="mobile":s<e.tablet?i="tablet":i="desktop";const n=l.shouldShowSidebar(i),o=document.getElementById("sidebar");o&&o.style.setProperty(`--sidebar-${i}-display`,n?"block":"none")}initOutlineVisibility(){this.updateOutlineVisibility();const e=()=>{window.swup?.hooks&&(window.swup.hooks.on("content:replace",()=>{this.removeOutline()}),window.swup.hooks.on("page:view",()=>{setTimeout(()=>this.updateOutlineVisibility(),150)}))};window.swup?e():document.addEventListener("swup:enable",e)}removeOutline(){const e=document.getElementById("article-outline-wrapper");if(!e)return;e.classList.add("hidden");const s=e.querySelector("article-outline");s&&s.remove()}updateOutlineVisibility(){const e=document.getElementById("article-outline-wrapper");if(!e)return;window.location.pathname.includes("/posts/")?setTimeout(()=>{const i=document.querySelector(".markdown-content, .custom-md, .prose");i?(this.createOutline(e,i),e.classList.remove("hidden")):e.classList.add("hidden")},150):e.classList.add("hidden")}createOutline(e,s){const i=s.querySelectorAll("h1, h2, h3, h4, h5, h6");if(i.length===0)return;const n=[];if(i.forEach(t=>{t.id&&n.push({depth:parseInt(t.tagName.substring(1)),slug:t.id,text:(t.textContent||"").replace(/#+\s*$/,"").trim()})}),n.length===0)return;let o=Math.min(...n.map(t=>t.depth));const d=3;let r=1;const c=`
				<article-outline class="block w-full">
					<div class="card-base max-h-[calc(100vh-6rem)] overflow-hidden flex flex-col">
						<div class="px-4 py-3 border-b border-[var(--line-divider)]">
							<div class="flex items-center gap-2 text-sm font-bold text-black/75 dark:text-white/75">
								<svg class="text-lg w-5 h-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
									<path d="M8 6h13v2H8V6zm0 5h13v2H8v-2zm0 5h13v2H8v-2zM4 6h2v2H4V6zm0 5h2v2H4v-2zm0 5h2v2H4v-2z"/>
								</svg>
								<span>文章大纲</span>
							</div>
						</div>
						<div class="outline-content overflow-y-auto overflow-x-hidden hide-scrollbar px-2 py-3 flex-1">
							${n.filter(t=>t.depth<o+d).map(t=>{const p=(t.depth-o)*1,a=t.depth===o,u=a?r++:null;return`
										<a 
											href="#${t.slug}"
											class="outline-item flex items-start gap-2 px-2 py-1.5 rounded hover:bg-[var(--btn-plain-bg-hover)] transition-colors"
											style="padding-left: ${p+.5}rem"
											data-heading-id="${t.slug}"
										>
											${a?`<span class="shrink-0 text-[var(--primary)] font-bold text-xs mt-0.5">${u}.</span>`:""}
											<span class="text-sm leading-relaxed flex-1 ${a?"text-black/90 dark:text-white/90 font-medium":"text-black/70 dark:text-white/70"}">
												${t.text}
											</span>
										</a>
									`}).join("")}
						</div>
					</div>
				</article-outline>
			`;e.innerHTML=c}}new h;
