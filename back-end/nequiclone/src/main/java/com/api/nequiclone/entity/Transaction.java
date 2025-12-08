package com.api.nequiclone.entity;

import java.math.BigDecimal;
import java.time.LocalDateTime;

import com.api.nequiclone.enums.TransactionStatus;
import com.api.nequiclone.enums.TransactionType;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
@Entity
@Table(name = "transactions")
public class Transaction {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "amount", nullable = false, precision = 19, scale = 2)
    private BigDecimal amount;

    @Enumerated(EnumType.STRING)
    @Column(name = "transaction_type", nullable = false)
    private TransactionType transactionType;

    @Column(name = "description", columnDefinition = "TEXT")
    private String description;

    @ManyToOne
    @JoinColumn(name = "account_id")
    private Account account; // Cuenta origen

    // Relaciones opcionales
    @ManyToOne
    @JoinColumn(name = "target_account_id", nullable = true)
    private Account targetAccount; // Solo para transferencias

    @ManyToOne
    @JoinColumn(name = "provider_id", nullable = true)
    private UtilityProvider provider; // Solo para pagos de servicios

    @ManyToOne
    @JoinColumn(name = "mobile_package_id", nullable = true)
    private MobilePackage mobilePackage; // Solo para paquetes móviles

    // Campos específicos
    private Long contractNumber;
    private String phoneNumber;
    private Long referenceNumber;

    @Column(name = "timestamp", nullable = false)
    private LocalDateTime timestamp;

    @Enumerated(EnumType.STRING)
    @Column(name = "status", nullable = false)
    private TransactionStatus status;
}
