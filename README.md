## SETUP

create .env file, fill in the blanks

```
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt

python3 setup.py            <!--look at the setup section below-->
python3 main.py
```

```
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Summarize the key findings of Jan 2026"}'
```

ngrok using

```
ngrok http 8000 \
  --host-header="localhost:8000" \
  --response-header-add="Access-Control-Allow-Origin: *" \
  --response-header-add="Access-Control-Allow-Headers: *" \
  --response-header-add="Access-Control-Allow-Methods: GET" \
  --response-header-add="Access-Control-Expose-Headers: *" \
  --response-header-add="Acess-Control-Allow-Headers: Ngrok-skip-browser-warning"
```

if you wanna tinker around with setting up your own chroma_db, tinker around with setup.py
delete chroma_db
this will create chrome_db again, it takes a little bit of time.. so yeah be patient

```
python3 setup.py
```

## ISSUES:

- not giving satisfactory answers. (eg if asked to summarize a month's data, it does not search up all the chunks and generates summary from them, just one or two, despite search_kwargs={"k": 10}. is it due to the fact how I have (gemini has) chunked the data? most probably idk)

- while doing setup, it is creating chunks of size greater than 1000 (why?)

## $$ code to get data from [this site](https://satp.org/terrorist-activity/india-jan-2026)

```
copy(
  $$(".more")
    .map(more => {
      const td = more.closest("td");
      const prevTdText = td?.previousElementSibling?.innerText.trim() || "";
      const moreText = more.innerText.trim();
      return `${prevTdText}, 2026\n${moreText}`.trim();
    })
    .filter(Boolean)
    .join("\n\n---\n\n")
);
```
