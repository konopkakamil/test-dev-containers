package com.qperior.springdevcontainer;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDateTime;

@RestController
public class MyRestController {

    @PostMapping("/test")
    public ResponseEntity<String> generateMessage(@RequestParam(required = false) Integer i) {
        var message = getMessage(i);
        return ResponseEntity.ok(message);
    }

    private String getMessage(Integer i) {
        if (i == null) {
            throw new IllegalStateException("Index cannot be null");
        }

        var now = LocalDateTime.now();
        var change = LocalDateTime.of(2024, 4, 1, 10, 10, 10);

        if (change.isBefore(now)) {
            return "hello world before";
        }

        return "hello world after";
    }
}
