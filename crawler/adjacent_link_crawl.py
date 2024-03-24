
class WikipediaCrawler:


  def scrape_process(self, url):
        
        # request the html content of the url 
        response = requests.get(url)
        if response.status_code == 200:

            # get the html content from the web page
            html_content = response.text

            # MANAGE LINKS TO OTHER PAGES

            # get all the links to other pages
            links = scrape_wiki.search_HTML(html_content)

            # add all of the links that have not been searched to the queue
            for link in links: 
                if not link in self.crawled_urls: 
                    self.crawl_queue.put(link)

            #MANAGE WEB PAGE CONTENT
            
            # get the image links and the text sections from the html
            image_urls, text_sections = parse_wiki.extract_html(html_content, url)

            # for each of the image urls, upsert them to the vector search client
            print(f"[scrape_process]: {url}, links: {len(links)} image urls: {len(image_urls)}")
            for image_url in image_urls[:20]:
                upsert_result = self.upsert_image_url(image_url, url)
                self.images_indexed +=1
                print(f"\timage: \033[1m{image_url[60:120]}\033[0m, result: {upsert_result}")
            print(f"total images indexed: {self.images_indexed}")


        # record that the scrape process has finished
        self.scrape_processes_completed += 1
            
            

    
    def crawler_process(self):
        while True: 
            try:
                #print(f"{multiprocessing.current_process().name}: ")

                # slow down for the scrape process if nescessary
                if len(self.crawled_urls) - self.scrape_processes_completed > 5:
                    continue

                # the url currently being scraped
                target_url = self.crawl_queue.get(timeout=60)
                
                # make sure that the target url has not already been scraped
                if target_url not in self.crawled_urls:

                    self.crawled_urls.add(target_url)
                    self.urls_crawled_from_session += 1

                    print(f"[crawler_process] url: \033[1m{target_url[27:80]}\033[0m, queue size: {self.crawl_queue.qsize()}, crawled urls session: {self.urls_crawled_from_session} crawled urls total: {len(self.crawled_urls)} scrape processes: {self.scrape_processes_completed}")

                    # save the progress every 100 urls
                    if len(self.crawled_urls) - self.last_save > save_frequency:
                        self.save_progress()
                        self.last_save = len(self.crawled_urls)

                    # process the web page in another thread
                    job = self.pool.submit(self.scrape_process, target_url)

            except Empty:
                print("crawl queue is empty, finishing process...")
                return
            except Exception as e:
                print("error")
                print(e)
                continue