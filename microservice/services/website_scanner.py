"""
Website scanner service for comprehensive webpage analysis and data extraction
"""
import asyncio
import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import sys

# Add the parent directory to the Python path so we can import browser_use
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from browser_use import Agent
from browser_use.browser import BrowserSession
from browser_use.dom.service import DomService
from utils.logger import setup_logger

logger = setup_logger()

class WebsiteScanner:
    """Enhanced website scanner with comprehensive scanning capabilities"""
    
    def __init__(self, llm):
        self.llm = llm
        self.scan_results = {}
        
    async def perform_comprehensive_scan(
        self, 
        url: str, 
        scan_type: str = "full",
        custom_selectors: Optional[List[str]] = None,
        extract_goals: Optional[List[str]] = None,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Perform comprehensive website scanning
        
        Args:
            url: URL to scan
            scan_type: Type of scan ("full", "content", "structure", "accessibility", "security", "performance")
            custom_selectors: Custom CSS selectors to extract data from
            extract_goals: Specific extraction goals for content analysis
            timeout: Scan timeout in seconds
            
        Returns:
            Dictionary containing scan results
        """
        logger.info(f"Starting {scan_type} scan for URL: {url}")
        
        try:
            # Initialize browser session with headless configuration
            from browser_use import BrowserProfile
            profile = BrowserProfile(headless=True)
            browser_session = BrowserSession(browser_profile=profile)
            await browser_session.start()
            
            page = await browser_session.get_current_page()
            
            # Navigate to the URL
            await page.goto(url, wait_until='networkidle')
            
            scan_results = {
                'url': url,
                'scan_type': scan_type,
                'timestamp': datetime.now().isoformat(),
                'status': 'completed',
                'data': {}
            }
            
            # Perform different types of scans based on scan_type
            if scan_type in ["full", "content"]:
                scan_results['data']['content'] = await self._extract_content_data(
                    page, browser_session, extract_goals
                )
                
            if scan_type in ["full", "structure"]:
                scan_results['data']['structure'] = await self._extract_structure_data(
                    page, browser_session
                )
                
            if scan_type in ["full", "accessibility"]:
                scan_results['data']['accessibility'] = await self._extract_accessibility_data(
                    page, browser_session
                )
                
            if scan_type in ["full", "security"]:
                scan_results['data']['security'] = await self._extract_security_data(
                    page, browser_session
                )
                
            if scan_type in ["full", "performance"]:
                scan_results['data']['performance'] = await self._extract_performance_data(
                    page, browser_session
                )
                
            if custom_selectors:
                scan_results['data']['custom_extraction'] = await self._extract_custom_data(
                    page, browser_session, custom_selectors
                )
            
            # Capture screenshot
            screenshot_path = await self._capture_screenshot(page)
            scan_results['screenshot_path'] = screenshot_path
            
            await browser_session.close()
            
            logger.info(f"Scan completed successfully for {url}")
            return scan_results
            
        except Exception as e:
            logger.error(f"Scan failed for {url}: {str(e)}")
            return {
                'url': url,
                'scan_type': scan_type,
                'timestamp': datetime.now().isoformat(),
                'status': 'failed',
                'error': str(e),
                'data': {}
            }
    
    async def _extract_content_data(
        self, 
        page, 
        browser_session: BrowserSession, 
        extract_goals: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Extract content-related data from the page"""
        content_data = {}
        
        try:
            # Basic page information
            content_data['title'] = await page.title()
            content_data['url'] = page.url
            content_data['meta_description'] = await page.locator('meta[name="description"]').get_attribute('content') or ""
            
            # Extract text content
            import markdownify
            html_content = await page.content()
            content_data['markdown_content'] = markdownify.markdownify(html_content, strip=['script', 'style'])
            
            # Extract headings structure
            headings = []
            for level in range(1, 7):
                heading_elements = await page.locator(f'h{level}').all()
                for element in heading_elements:
                    text = await element.inner_text()
                    if text.strip():
                        headings.append({
                            'level': level,
                            'text': text.strip(),
                            'tag': f'h{level}'
                        })
            content_data['headings'] = headings
            
            # Extract links
            links = []
            link_elements = await page.locator('a[href]').all()
            for element in link_elements:
                href = await element.get_attribute('href')
                text = await element.inner_text()
                if href:
                    links.append({
                        'url': href,
                        'text': text.strip(),
                        'internal': href.startswith('/') or page.url.split('/')[2] in href
                    })
            content_data['links'] = links[:50]  # Limit to first 50 links
            
            # Extract images
            images = []
            img_elements = await page.locator('img').all()
            for element in img_elements:
                src = await element.get_attribute('src')
                alt = await element.get_attribute('alt') or ""
                if src:
                    images.append({
                        'src': src,
                        'alt': alt
                    })
            content_data['images'] = images[:20]  # Limit to first 20 images
            
            # Custom goal-based extraction using LLM
            if extract_goals and self.llm:
                goal_extractions = {}
                for goal in extract_goals:
                    try:
                        # Use the extract_content functionality
                        from langchain_core.prompts import PromptTemplate
                        
                        prompt = 'Your task is to extract the content of the page. You will be given a page and a goal and you should extract all relevant information around this goal from the page. If the goal is vague, summarize the page. Respond in json format. Extraction goal: {goal}, Page: {page}'
                        template = PromptTemplate(input_variables=['goal', 'page'], template=prompt)
                        
                        output = await self.llm.ainvoke(
                            template.format(goal=goal, page=content_data['markdown_content'][:8000])  # Limit content length
                        )
                        goal_extractions[goal] = output.content
                    except Exception as e:
                        logger.warning(f"Failed to extract content for goal '{goal}': {str(e)}")
                        goal_extractions[goal] = f"Extraction failed: {str(e)}"
                
                content_data['goal_extractions'] = goal_extractions
            
        except Exception as e:
            logger.error(f"Error extracting content data: {str(e)}")
            content_data['error'] = str(e)
            
        return content_data
    
    async def _extract_structure_data(self, page, browser_session: BrowserSession) -> Dict[str, Any]:
        """Extract structural data from the page"""
        structure_data = {}
        
        try:
            # DOM structure analysis
            dom_service = DomService(page)
            dom_state = await dom_service.get_clickable_elements(highlight_elements=False)
            
            structure_data['clickable_elements_count'] = len(dom_state.selector_map)
            structure_data['dom_depth'] = self._calculate_dom_depth(dom_state.element_tree)
            
            # Form analysis
            forms = []
            form_elements = await page.locator('form').all()
            for form in form_elements:
                form_data = {
                    'action': await form.get_attribute('action') or "",
                    'method': await form.get_attribute('method') or "GET",
                    'inputs': []
                }
                
                input_elements = await form.locator('input, select, textarea').all()
                for input_elem in input_elements:
                    input_data = {
                        'type': await input_elem.get_attribute('type') or 'text',
                        'name': await input_elem.get_attribute('name') or "",
                        'id': await input_elem.get_attribute('id') or "",
                        'required': await input_elem.get_attribute('required') is not None
                    }
                    form_data['inputs'].append(input_data)
                
                forms.append(form_data)
            
            structure_data['forms'] = forms
            
            # Technology detection
            technologies = await self._detect_technologies(page)
            structure_data['technologies'] = technologies
            
        except Exception as e:
            logger.error(f"Error extracting structure data: {str(e)}")
            structure_data['error'] = str(e)
            
        return structure_data
    
    async def _extract_accessibility_data(self, page, browser_session: BrowserSession) -> Dict[str, Any]:
        """Extract accessibility-related data"""
        accessibility_data = {}
        
        try:
            # Get accessibility tree
            ax_tree = await page.accessibility.snapshot(interesting_only=True)
            accessibility_data['ax_tree_available'] = ax_tree is not None
            
            if ax_tree:
                accessibility_data['ax_elements_count'] = self._count_ax_elements(ax_tree)
            
            # Check for common accessibility features
            alt_missing = await page.locator('img:not([alt])').count()
            accessibility_data['images_without_alt'] = alt_missing
            
            # Check for heading structure
            h1_count = await page.locator('h1').count()
            accessibility_data['h1_count'] = h1_count
            accessibility_data['proper_heading_structure'] = h1_count == 1
            
            # Check for ARIA labels
            aria_labels = await page.locator('[aria-label], [aria-labelledby]').count()
            accessibility_data['elements_with_aria_labels'] = aria_labels
            
        except Exception as e:
            logger.error(f"Error extracting accessibility data: {str(e)}")
            accessibility_data['error'] = str(e)
            
        return accessibility_data
    
    async def _extract_security_data(self, page, browser_session: BrowserSession) -> Dict[str, Any]:
        """Extract security-related data"""
        security_data = {}
        
        try:
            # Check HTTPS
            security_data['is_https'] = page.url.startswith('https://')
            
            # Check for mixed content
            mixed_content_scripts = await page.locator('script[src^="http://"]').count()
            mixed_content_images = await page.locator('img[src^="http://"]').count()
            security_data['mixed_content_scripts'] = mixed_content_scripts
            security_data['mixed_content_images'] = mixed_content_images
            
            # Check for security headers (basic check)
            response = await page.goto(page.url)
            headers = response.headers
            
            security_headers = {
                'content-security-policy': 'content-security-policy' in headers,
                'x-frame-options': 'x-frame-options' in headers,
                'x-content-type-options': 'x-content-type-options' in headers,
                'strict-transport-security': 'strict-transport-security' in headers
            }
            security_data['security_headers'] = security_headers
            
        except Exception as e:
            logger.error(f"Error extracting security data: {str(e)}")
            security_data['error'] = str(e)
            
        return security_data
    
    async def _extract_performance_data(self, page, browser_session: BrowserSession) -> Dict[str, Any]:
        """Extract performance-related data"""
        performance_data = {}
        
        try:
            # Page load metrics
            performance_timing = await page.evaluate("""
                () => {
                    const timing = performance.timing;
                    return {
                        domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
                        loadComplete: timing.loadEventEnd - timing.navigationStart,
                        domInteractive: timing.domInteractive - timing.navigationStart
                    };
                }
            """)
            performance_data['timing'] = performance_timing
            
            # Resource counts
            resource_count = await page.evaluate("""
                () => {
                    const resources = performance.getEntriesByType('resource');
                    return {
                        total: resources.length,
                        scripts: resources.filter(r => r.name.includes('.js')).length,
                        stylesheets: resources.filter(r => r.name.includes('.css')).length,
                        images: resources.filter(r => /\\.(png|jpg|jpeg|gif|svg|webp)/.test(r.name)).length
                    };
                }
            """)
            performance_data['resources'] = resource_count
            
        except Exception as e:
            logger.error(f"Error extracting performance data: {str(e)}")
            performance_data['error'] = str(e)
            
        return performance_data
    
    async def _extract_custom_data(
        self, 
        page, 
        browser_session: BrowserSession, 
        custom_selectors: List[str]
    ) -> Dict[str, Any]:
        """Extract data using custom CSS selectors"""
        custom_data = {}
        
        for selector in custom_selectors:
            try:
                elements = await page.locator(selector).all()
                extracted_items = []
                
                for element in elements[:10]:  # Limit to 10 elements per selector
                    text = await element.inner_text()
                    html = await element.inner_html()
                    extracted_items.append({
                        'text': text.strip(),
                        'html': html[:500]  # Limit HTML length
                    })
                
                custom_data[selector] = extracted_items
                
            except Exception as e:
                logger.warning(f"Failed to extract data for selector '{selector}': {str(e)}")
                custom_data[selector] = {'error': str(e)}
        
        return custom_data
    
    async def _capture_screenshot(self, page) -> str:
        """Capture screenshot of the page"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_path = f"/tmp/screenshot_{timestamp}.png"
            await page.screenshot(path=screenshot_path, full_page=True)
            return screenshot_path
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {str(e)}")
            return ""
    
    async def _detect_technologies(self, page) -> List[str]:
        """Detect technologies used on the page"""
        technologies = []
        
        try:
            # Check for common frameworks and libraries
            tech_checks = await page.evaluate("""
                () => {
                    const techs = [];
                    
                    // Check for common global variables
                    if (window.jQuery || window.$) techs.push('jQuery');
                    if (window.React) techs.push('React');
                    if (window.Vue) techs.push('Vue.js');
                    if (window.angular) techs.push('Angular');
                    if (window.bootstrap) techs.push('Bootstrap');
                    
                    // Check for meta tags
                    const generator = document.querySelector('meta[name="generator"]');
                    if (generator) techs.push(`Generator: ${generator.content}`);
                    
                    return techs;
                }
            """)
            technologies.extend(tech_checks)
            
        except Exception as e:
            logger.error(f"Error detecting technologies: {str(e)}")
            
        return technologies
    
    def _calculate_dom_depth(self, element_tree) -> int:
        """Calculate the depth of the DOM tree"""
        if not element_tree or not hasattr(element_tree, 'children'):
            return 0
        
        if not element_tree.children:
            return 1
        
        return 1 + max(self._calculate_dom_depth(child) for child in element_tree.children)
    
    def _count_ax_elements(self, ax_tree) -> int:
        """Count elements in accessibility tree"""
        if not ax_tree:
            return 0
        
        count = 1
        for child in ax_tree.get('children', []):
            count += self._count_ax_elements(child)
        
        return count
