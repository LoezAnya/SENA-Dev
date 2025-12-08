package com.api.nequiclone.controller;

import java.math.BigDecimal;
import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import com.api.nequiclone.dto.request.UtilityPaymentRequestDTO;
import com.api.nequiclone.entity.Transaction;
import com.api.nequiclone.service.interfaces.TransactionService;

@RestController
@RequestMapping("/api/v1/transactions")
public class TransactionController {

    private final TransactionService transactionService;

    public TransactionController(TransactionService transactionService) {
        this.transactionService = transactionService;
    }

    /**
     * Endpoint para depositar dinero en una cuenta.
     * POST /api/transactions/deposit
     * Body: { "accountId": 1, "amount": 100.00, "description": "Depósito inicial" }
     */
    @PostMapping("/deposit")
    public ResponseEntity<?> deposit(@RequestParam Long accountId,
            @RequestParam BigDecimal amount,
            @RequestParam(required = false, defaultValue = "Depósito") String description) {
        try {
            Transaction tx = transactionService.depositMoney(accountId, amount, description);
            return ResponseEntity.status(HttpStatus.CREATED).body(tx);
        } catch (IllegalStateException e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(e.getMessage());
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Error interno: " + e.getMessage());
        }
    }

    /**
     * Endpoint para transferir dinero entre cuentas.
     * POST /api/transactions/transfer
     * Body: { "fromAccountId": 1, "toAccountNumber": "AC...", "amount": 50.00,
     * "description": "..." }
     */
    @PostMapping("/transfer")
    public ResponseEntity<?> transfer(@RequestParam Long fromAccountId,
            @RequestParam String toAccountNumber,
            @RequestParam BigDecimal amount,
            @RequestParam(required = false, defaultValue = "Transferencia") String description) {
        try {
            Transaction tx = transactionService.transferMoney(fromAccountId, toAccountNumber, amount, description);
            return ResponseEntity.status(HttpStatus.CREATED).body(tx);
        } catch (IllegalStateException e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(e.getMessage());
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Error interno: " + e.getMessage());
        }
    }

    /**
     * Endpoint para comprar un paquete móvil.
     * POST /api/transactions/mobile-purchase
     * Body params: accountId, packageId, phoneNumber
     */
    @PostMapping("/mobile-purchase")
    public ResponseEntity<?> purchaseMobilePackage(@RequestParam Long accountId,
            @RequestParam Long packageId,
            @RequestParam String phoneNumber) {
        try {
            Transaction tx = transactionService.purchaseMobilePackage(accountId, packageId, phoneNumber);
            return ResponseEntity.status(HttpStatus.CREATED).body(tx);
        } catch (IllegalStateException e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(e.getMessage());
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Error interno: " + e.getMessage());
        }
    }

    /**
     * Endpoint para pagar servicios públicos.
     * POST /api/transactions/utility-payment
     * Body: { "accountId": 1, "paymentRequest": { "providerId": 1, "amount": 75.50,
     * "contractNumber": "12345", "referenceNumber": "REF123" } }
     */
    @PostMapping("/utility-payment/{accountId}")
    public ResponseEntity<?> payUtility(@PathVariable Long accountId,
            @RequestBody UtilityPaymentRequestDTO paymentRequest) {
        try {
            Transaction tx = transactionService.payUtilityBill(accountId, paymentRequest);
            return ResponseEntity.status(HttpStatus.CREATED).body(tx);
        } catch (IllegalStateException e) {
            return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(e.getMessage());
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Error interno: " + e.getMessage());
        }
    }

    /**
     * Endpoint para obtener el historial de transacciones de una cuenta.
     * GET /api/transactions/history/{accountId}
     */
    @GetMapping("/history/{accountId}")
    public ResponseEntity<?> getTransactionHistory(@PathVariable Long accountId) {
        try {
            List<Transaction> transactions = transactionService.getTransactionHistoryForAccount(accountId);
            return ResponseEntity.ok(transactions);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Error interno: " + e.getMessage());
        }
    }

    /**
     * Endpoint para obtener una transacción específica.
     * GET /api/transactions/{transactionId}
     */
    @GetMapping("/{transactionId}")
    public ResponseEntity<?> getTransaction(@PathVariable Long transactionId) {
        try {
            Transaction tx = transactionService.getTransactionById(transactionId);
            return ResponseEntity.ok(tx);
        } catch (IllegalStateException e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body(e.getMessage());
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Error interno: " + e.getMessage());
        }
    }
}