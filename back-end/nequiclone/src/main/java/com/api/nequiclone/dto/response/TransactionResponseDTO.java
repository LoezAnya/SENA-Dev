package com.api.nequiclone.dto.response;

import java.math.BigDecimal;
import java.time.LocalDateTime;

import com.api.nequiclone.entity.Transaction;

import lombok.Data;

@Data
public class TransactionResponseDTO {
    private Long id;
    private BigDecimal amount;
    private String description;
    private String transactionType;
    private String status;
    private LocalDateTime timestamp;
    private String accountNumber;
    private String targetAccountNumber;


        public TransactionResponseDTO(Transaction transaction) {
        this.id = transaction.getId();
        this.amount = transaction.getAmount();
        this.description = transaction.getDescription();
        this.transactionType = transaction.getTransactionType().name();
        this.status = transaction.getStatus().name();
        this.timestamp = transaction.getTimestamp();
        this.accountNumber = transaction.getAccount().getAccountNumber();
        
        if (transaction.getTargetAccount() != null) {
            this.targetAccountNumber = transaction.getTargetAccount().getAccountNumber();
        }
    }
}
