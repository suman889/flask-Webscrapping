import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests as rq
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import pandas as pd
from time import sleep

headers = {
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Referer': 'http://www.wikipedia.org/',
    'Connection': 'keep-alive',
}

app = Flask(__name__)


@app.route('/', methods=['GET'])  # route to display the home page
@cross_origin()
def homePage():
    return render_template("index.html")


@app.route('/review', methods=['POST', 'GET'])  # route to show the review comments in a web UI
@cross_origin()
def index():
    name=[]
    rating=[]
    comment=[]
    review=[]
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ", "")
            amazon_url = "https://www.amazon.in/s?k=" + searchString
            sleep(2)
            uClient = uReq(amazon_url)
            amazonPage = uClient.read()
            uClient.close()
            sleep(2)
            amazon_html = bs(amazonPage, "html.parser")
            amazon_html
            bigboxes=amazon_html.find_all('h2',{'class':'a-size-mini a-spacing-none a-color-base s-line-clamp-2'})
            box=bigboxes[0]
            prod_link='https://www.amazon.in' + box.a['href']
            review_link=rq.get(prod_link,headers=headers)
            soup=bs(review_link.text,'html.parser')
            # uc=uReq(prod_link)
            # page1=uc.read()
            # uc.close()
            # sleep(2)
            # soup=bs(page1,'html.parser')
            for i in soup.findAll('a',{'data-hook':'see-all-reviews-link-foot'}):
                li=i.get('href')
                prod=rq.get('https://www.amazon.in'+ li)
                aa=bs(prod.text,'html.parser')
        
            try:
                for j in aa.find_all('div',{'class':'a-profile-content'}):
                        n=j.get_text()
                        name.append(n)
            except:
                name.append(' ')
            try:
                for k in aa.find_all('i',{'data-hook':'review-star-rating'}):
                    r=k.get_text()
                    rating.append(r)
            except:
                rating.append(' ')
            try:
                for l in aa.find_all('a',{'data-hook':'review-title'}):
                    ch=l.get_text()
                    comment.append(ch)
                    comment[:]=[co.lstrip("\n") for co in comment]
                    comment[:]=[co.rstrip("\n") for co in comment]
            except:
                comment.append(' ')
            try:
                for m in aa.find_all('span',{'data-hook':'review-body'}):
                    re=m.get_text()
                    review.append(re)
                    review[:]=[coo.lstrip("\n") for coo in review]
                    review[:]=[coo.rstrip("\n") for coo in review]
                    review[:]=[cooo.lstrip(" \xa0") for cooo in review]
            except:
                review.append(' ')  

            reviews = {"Product":searchString,"Name": name[2:], "Rating": rating, "CommentHead": comment,
                                    "Comment": review}
            df=pd.DataFrame(reviews)
            # print(df)
            return render_template('results.html',tables=[df.to_html(classes='data',index=False)],titles=df.columns.values)
        except Exception as e:
            print(e)
        return render_template('results.html')

    else:
        return render_template('index.html')

# port = int(os.getenv("PORT"))
if __name__ == "__main__":
    # app.run(host='0.0.0.0', port=5000)
    # app.run(host='0.0.0.0', port=port)
    app.run(host='127.0.0.1', port=8001, debug=True)

