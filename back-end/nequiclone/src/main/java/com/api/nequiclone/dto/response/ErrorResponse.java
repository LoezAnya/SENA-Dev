package com.api.nequiclone.dto.response;

import java.time.LocalDateTime;

import lombok.Data;

@Data
public class ErrorResponse {
    private String message;
    private LocalDateTime timestamp;
    
    public ErrorResponse(String message) {
        this.message = message;
        this.timestamp = LocalDateTime.now();
    }
}
