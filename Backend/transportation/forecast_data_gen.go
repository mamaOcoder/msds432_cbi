package transportation

import (
	"fmt"
	"time"
)

func forecastUrls(base_urls []string) []string {
	var query_urls []string

	url_limit := 300

	year := 2024
	months := []time.Month{time.February}

	for _, turl := range base_urls {
		for _, month := range months {
			daysInMonth := time.Date(year, month+1, 0, 0, 0, 0, 0, time.UTC).Day()
			for day := 1; day <= daysInMonth; day++ {
				dateString := fmt.Sprintf("2024-%02d-%02d", month, day)
				taxi_url := fmt.Sprintf("%s?$limit=%d&$where=trip_start_timestamp>='%sT00:00:00.000'+AND+trip_start_timestamp<='%sT23:59:59.999'", turl, url_limit, dateString, dateString)
				query_urls = append(query_urls, taxi_url)
			}
		}

	}

	return query_urls
}
