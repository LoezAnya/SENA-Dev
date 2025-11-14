package com.api.nequiclone.entity;

import java.math.BigDecimal;
import java.time.LocalDateTime;

import com.api.nequiclone.enums.TransactionStatus;
import com.api.nequiclone.enums.TransactionType;

import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@Entity
@Table(name = "transactions")
public class Transaction {

    private Long id;

    private BigDecimal amount;
    
    private TransactionType transactionType;

    private String description;

    private Long fromAccountId;

    private Long toAccountId;

    private LocalDateTime timestamp;

    private TransactionStatus status; 
}
