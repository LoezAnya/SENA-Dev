package com.api.nequiclone.service.interfaces;

import java.math.BigDecimal;

import com.api.nequiclone.entity.Account;

public interface AccountService {

    Account createAccount(Account account, Long userId);

    Account getAccountById(Long id);

    Account getAccountByNumber(String accountNumber);

    Account updateAccountNumber(Account account);

    Account updateAccountBalance(Long accountId, BigDecimal newBalance); 

    void deactivateAccount(Long accountId);
}
