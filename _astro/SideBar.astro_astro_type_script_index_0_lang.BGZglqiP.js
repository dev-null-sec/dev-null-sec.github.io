import{w as m}from"./widget-manager.C8kMla_W.js";import"./config.CHaB2CpH.js";class v{outlineScrollHandler;outlineResizeHandler;constructor(){this.init(),this.initOutlineVisibility()}init(){this.updateResponsiveDisplay(),window.addEventListener("resize",()=>this.updateResponsiveDisplay())}updateResponsiveDisplay(){const e=m.getBreakpoints(),n=window.innerWidth;let i;n<e.mobile?i="mobile":n<e.tablet?i="tablet":i="desktop";const s=m.shouldShowSidebar(i),l=document.getElementById("sidebar");l&&l.style.setProperty(`--sidebar-${i}-display`,s?"block":"none")}initOutlineVisibility(){this.updateOutlineVisibility();const e=()=>{window.swup?.hooks&&(window.swup.hooks.on("content:replace",()=>{this.removeOutline()}),window.swup.hooks.on("page:view",()=>{setTimeout(()=>this.updateOutlineVisibility(),150)}))};window.swup?e():document.addEventListener("swup:enable",e)}toggleWidgetsForArticle(){const e=document.getElementById("sidebar");if(!e)return;const n=e.querySelector(":scope > .flex.flex-col.w-full.gap-4");n&&(n.style.display="");const i=document.getElementById("sidebar-sticky");if(i){const s=i.children;for(let l=0;l<s.length;l++){const r=s[l];r.id!=="article-outline-wrapper"&&(r.style.display="")}}}showAllWidgets(){const e=document.getElementById("sidebar");if(!e)return;const n=e.querySelector(":scope > .flex.flex-col.w-full.gap-4");n&&(n.style.display="");const i=document.getElementById("sidebar-sticky");if(i){const s=i.children;for(let l=0;l<s.length;l++){const r=s[l];r.id!=="article-outline-wrapper"&&(r.style.display="")}}}removeOutline(){const e=document.getElementById("article-outline-wrapper");if(!e)return;this.cleanupOutlineTracking(),e.classList.add("hidden");const n=e.querySelector("article-outline");n&&n.remove()}updateOutlineVisibility(){const e=document.getElementById("article-outline-wrapper");if(!e)return;window.location.pathname.includes("/posts/")?(this.toggleWidgetsForArticle(),setTimeout(()=>{const i=document.querySelector(".markdown-content, .custom-md, .prose");i?(this.createOutline(e,i),e.classList.remove("hidden")):(this.cleanupOutlineTracking(),e.classList.add("hidden"))},150)):(this.showAllWidgets(),this.cleanupOutlineTracking(),e.classList.add("hidden"))}createOutline(e,n){const i=n.querySelectorAll("h1, h2, h3, h4, h5, h6");if(i.length===0){this.cleanupOutlineTracking(),e.classList.add("hidden");return}const s=[];if(i.forEach(t=>{t.id&&s.push({depth:parseInt(t.tagName.substring(1)),slug:t.id,text:(t.textContent||"").replace(/#+\s*$/,"").trim()})}),s.length===0)return;let l=Math.min(...s.map(t=>t.depth));const r=3;let c=1;const u=`
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
							${s.filter(t=>t.depth<l+r).map(t=>{const o=(t.depth-l)*1,d=t.depth===l,h=d?c++:null;return`
										<a 
											href="#${t.slug}"
											class="outline-item flex items-start gap-2 px-2 py-1.5 rounded hover:bg-[var(--btn-plain-bg-hover)] transition-colors"
											style="padding-left: ${o+.5}rem"
											data-heading-id="${t.slug}"
										>
											${d?`<span class="shrink-0 text-[var(--primary)] font-bold text-xs mt-0.5">${h}.</span>`:""}
											<span class="text-sm leading-relaxed flex-1 ${d?"text-black/90 dark:text-white/90 font-medium":"text-black/70 dark:text-white/70"}">
												${t.text}
											</span>
										</a>
									`}).join("")}
						</div>
					</div>
				</article-outline>
			`;e.innerHTML=u,this.initOutlineTracking(e,n)}cleanupOutlineTracking(){this.outlineScrollHandler&&(window.removeEventListener("scroll",this.outlineScrollHandler),document.removeEventListener("scroll",this.outlineScrollHandler,!0),this.outlineScrollHandler=void 0),this.outlineResizeHandler&&(window.removeEventListener("resize",this.outlineResizeHandler),this.outlineResizeHandler=void 0)}initOutlineTracking(e,n){this.cleanupOutlineTracking();const i=Array.from(e.querySelectorAll(".outline-item[data-heading-id]")),s=i.map(t=>{const a=t.dataset.headingId,o=a?n.querySelector(`#${CSS.escape(a)}`):null;return o?{item:t,heading:o}:null}).filter(t=>!!t);if(s.length===0){this.cleanupOutlineTracking(),e.classList.add("hidden");return}const l=t=>{for(const p of i){const g=p===t;p.classList.toggle("is-active",g),g?p.setAttribute("aria-current","true"):p.removeAttribute("aria-current")}const a=e.querySelector(".outline-content");if(!a)return;const o=a.getBoundingClientRect(),d=t.getBoundingClientRect(),h=d.top<o.top,f=d.bottom>o.bottom;(h||f)&&a.scrollTo({top:a.scrollTop+d.top-o.top-o.height/3,behavior:"smooth"})},r=()=>{const t=Math.min(240,window.innerHeight*.32),a=window.scrollY+t;let o=s[0];for(const d of s)if(d.heading.getBoundingClientRect().top+window.scrollY<=a)o=d;else break;l(o.item)};let c=!1;const u=()=>{c||(c=!0,window.requestAnimationFrame(()=>{c=!1,r()}))};this.outlineScrollHandler=u,this.outlineResizeHandler=u,window.addEventListener("scroll",this.outlineScrollHandler,{passive:!0}),document.addEventListener("scroll",this.outlineScrollHandler,{capture:!0,passive:!0}),window.addEventListener("resize",this.outlineResizeHandler);for(const{item:t}of s)t.addEventListener("click",()=>{l(t)});r()}}new v;
