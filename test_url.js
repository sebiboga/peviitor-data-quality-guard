const puppeteer = require('puppeteer');

(async () => {
    const browser = await puppeteer.launch({headless: true, args: ['--no-sandbox', '--disable-setuid-sandbox']});
    const page = await browser.newPage();
    try {
        const url = process.env.JOB_URL || '';
        console.log('OPENING PAGE WITH PUPPETEER...');
        await page.goto(url, {timeout: 15000});
        await new Promise(r => setTimeout(r, 3000));
        
        console.log('URL:', url);
        const isAnofm = url.includes('anofm.ro');
        
        if (isAnofm) {
            console.log('DETECTED: ANOFM link - check ONLY 404');
            console.log('RESULT: ACTIVE (ANOFM job)');
            console.log('DECISION: Continue validation');
            require('fs').writeFileSync('/tmp/url_status.txt', 'ACTIVE');
        } else {
            const text = await page.evaluate(() => document.body.innerText);
            
            const expiredKeywords = ['no longer available','expired','404','job filled','ocupat','închis','similar jobs','joburi similare','anunt expirat','locul nu mai este disponibil','oferta a expirat','no longer active'];
            const isExpired = expiredKeywords.some(i => text.toLowerCase().includes(i));
            
            const isJob = text.toLowerCase().includes('responsabilit') || 
                         text.toLowerCase().includes('requirement') || 
                         text.toLowerCase().includes('apply') ||
                         text.toLowerCase().includes('candidat');
            
            if (isExpired) {
                console.log('RESULT: EXPIRED');
                console.log('DECISION: DELETE from Solr');
                require('fs').writeFileSync('/tmp/url_status.txt', 'EXPIRED');
            } else if (isJob) {
                console.log('RESULT: ACTIVE');
                console.log('DECISION: Continue validation');
                require('fs').writeFileSync('/tmp/url_status.txt', 'ACTIVE');
            } else {
                console.log('RESULT: NOT_A_JOB');
                console.log('DECISION: DELETE from Solr');
                require('fs').writeFileSync('/tmp/url_status.txt', 'NOT_A_JOB');
            }
        }
    } catch (e) {
        if (e.message.includes('404') || e.message.includes('net::ERR')) {
            console.log('RESULT: EXPIRED (404/Network Error)');
            console.log('DECISION: DELETE from Solr');
            require('fs').writeFileSync('/tmp/url_status.txt', 'EXPIRED');
        } else {
            console.log('ERROR:', e.message);
            require('fs').writeFileSync('/tmp/url_status.txt', 'ERROR');
        }
    } finally {
        await browser.close();
    }
})();
