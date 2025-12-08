package com.api.nequiclone.service.interfaces;

import java.math.BigDecimal;

import com.api.nequiclone.entity.Account;
import com.api.nequiclone.entity.User;

public interface AccountService {

    Account createAccount(User user);

    Account getAccountByUserId(Long userId);

    Account getAccountById(Long id);

    Account getAccountByNumber(String accountNumber);

    Account updateAccountNumber(Account account);

    Account updateAccountBalance(Long accountId, BigDecimal newBalance); 

    void deactivateAccount(Long accountId);
}
