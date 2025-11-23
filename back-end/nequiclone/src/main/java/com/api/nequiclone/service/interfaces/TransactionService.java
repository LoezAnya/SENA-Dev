package com.api.nequiclone.service.interfaces;

import java.math.BigDecimal;
import java.util.List;

import com.api.nequiclone.dto.request.UtilityPaymentRequestDTO;
import com.api.nequiclone.entity.Transaction;

public interface TransactionService {
    
    Transaction depositMoney(Long accountId, BigDecimal amount, String description);

    Transaction transferMoney(Long fromAccountId, String toAccountNumber, BigDecimal amount, String description);

    Transaction purchaseMobilePackage(Long accountId, Long packageId, String phoneNumber);

    Transaction payUtilityBill(Long accountId, UtilityPaymentRequestDTO paymentRequest); 

    List<Transaction> getTransactionHistoryForAccount(Long accountId);

    Transaction getTransactionById(Long id);
}
