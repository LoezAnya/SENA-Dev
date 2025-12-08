package com.api.nequiclone.service.implementation;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;


import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.api.nequiclone.dto.request.UtilityPaymentRequestDTO;
import com.api.nequiclone.entity.Account;
import com.api.nequiclone.entity.MobilePackage;
import com.api.nequiclone.entity.Transaction;
import com.api.nequiclone.entity.UtilityProvider;
import com.api.nequiclone.enums.TransactionStatus;
import com.api.nequiclone.enums.TransactionType;
import com.api.nequiclone.repository.AccountRepository;
import com.api.nequiclone.repository.MobilePackageRepository;
import com.api.nequiclone.repository.TransactionRepository;
import com.api.nequiclone.repository.UtilityProviderRepository;
import com.api.nequiclone.service.interfaces.TransactionService;

@Service
public class TransactionServiceImpl implements TransactionService {

    private final AccountRepository accountRepository;
    private final TransactionRepository transactionRepository;
    private final MobilePackageRepository mobilePackageRepository;
    private final UtilityProviderRepository utilityProviderRepository;
    
    public TransactionServiceImpl(AccountRepository accountRepository,
                                  TransactionRepository transactionRepository,
                                  MobilePackageRepository mobilePackageRepository,
                                  UtilityProviderRepository utilityProviderRepository) {
        this.accountRepository = accountRepository;
        this.transactionRepository = transactionRepository;
        this.mobilePackageRepository = mobilePackageRepository;
        this.utilityProviderRepository = utilityProviderRepository;
    }

    /**
     * Deposita dinero en la cuenta (incrementa balance y registra transacción).
     * Usa los campos y enums de la entidad Transaction.
     */
    @Override
    @Transactional
    public Transaction depositMoney(Long accountId, BigDecimal amount, String description) {
        Account account = accountRepository.findById(accountId)
                .orElseThrow(() -> new IllegalStateException("Cuenta no encontrada: " + accountId));

        account.setBalance(account.getBalance().add(amount));
        accountRepository.save(account);

        Transaction tx = new Transaction();
        tx.setAccount(account);
        tx.setAmount(amount);
        tx.setDescription(description);
        tx.setTransactionType(TransactionType.DEPOSIT);
        tx.setTimestamp(LocalDateTime.now());
        tx.setStatus(TransactionStatus.COMPLETED);
        return transactionRepository.save(tx);
    }

    /**
     * Transfiere dinero de una cuenta a otra (por número de cuenta).
     * Registra transfer con targetAccount y status.
     */
    @Override
    @Transactional
    public Transaction transferMoney(Long fromAccountId, String toAccountNumber, BigDecimal amount, String description) {
        Account from = accountRepository.findById(fromAccountId)
                .orElseThrow(() -> new IllegalStateException("Cuenta origen no encontrada: " + fromAccountId));
        Account to = accountRepository.findByAccountNumber(toAccountNumber)
                .orElseThrow(() -> new IllegalStateException("Cuenta destino no encontrada: " + toAccountNumber));

        if (from.getBalance().compareTo(amount) < 0) {
            throw new IllegalStateException("Saldo insuficiente");
        }

        from.setBalance(from.getBalance().subtract(amount));
        to.setBalance(to.getBalance().add(amount));
        accountRepository.save(from);
        accountRepository.save(to);

        Transaction tx = new Transaction();
        tx.setAccount(from);
        tx.setTargetAccount(to);
        tx.setAmount(amount);
        tx.setDescription(description);
        tx.setTransactionType(TransactionType.TRANSFER);
        tx.setTimestamp(LocalDateTime.now());
        tx.setStatus(TransactionStatus.COMPLETED);
        return transactionRepository.save(tx);
    }

    /**
     * Compra de paquete móvil: valida saldo, descuenta y registra transacción.
     * Guarda referencia al MobilePackage y al phoneNumber.
     */
    @Override
    @Transactional
    public Transaction purchaseMobilePackage(Long accountId, Long packageId, String phoneNumber) {
        Account account = accountRepository.findById(accountId)
                .orElseThrow(() -> new IllegalStateException("Cuenta no encontrada: " + accountId));
        MobilePackage mp = mobilePackageRepository.findById(packageId)
                .orElseThrow(() -> new IllegalStateException("Paquete no encontrado: " + packageId));

        BigDecimal price = mp.getPrice();
        if (account.getBalance().compareTo(price) < 0) {
            throw new IllegalStateException("Saldo insuficiente para comprar paquete");
        }

        account.setBalance(account.getBalance().subtract(price));
        accountRepository.save(account);

        Transaction tx = new Transaction();
        tx.setAccount(account);
        tx.setMobilePackage(mp);
        tx.setPhoneNumber(phoneNumber);
        tx.setAmount(price);
        tx.setDescription("Compra paquete móvil: " + mp.getName() + " para " + phoneNumber);
        tx.setTransactionType(TransactionType.MOBILE_PACKAGE);
        tx.setTimestamp(LocalDateTime.now());
        tx.setStatus(TransactionStatus.COMPLETED);
        return transactionRepository.save(tx);
    }

    /**
     * Pago de servicios públicos: valida y registra transacción.
     * Usa los campos contractNumber/referenceNumber y opcionalmente provider si se resuelve.
     */
    @Override
    @Transactional
    public Transaction payUtilityBill(Long accountId, UtilityPaymentRequestDTO paymentRequest) {
        Account account = accountRepository.findById(accountId)
                .orElseThrow(() -> new IllegalStateException("Cuenta no encontrada: " + accountId));
        BigDecimal amount = paymentRequest.getAmount();

        if (account.getBalance().compareTo(amount) < 0) {
            throw new IllegalStateException("Saldo insuficiente para el pago");
        }

        account.setBalance(account.getBalance().subtract(amount));
        accountRepository.save(account);
        UtilityProvider provider = utilityProviderRepository.findById(paymentRequest.getProviderId())
                .orElseThrow(() -> new IllegalStateException("Proveedor no encontrado: " + paymentRequest.getProviderId()));
        Transaction tx = new Transaction();
        tx.setAccount(account);
        tx.setAmount(amount);
        tx.setDescription("Pago servicio: " + provider.getName());
        
        tx.setReferenceNumber(paymentRequest.getContractNumber());
        tx.setContractNumber(paymentRequest.getContractNumber());
        tx.setTransactionType(TransactionType.UTILITY_BILL);
        tx.setTimestamp(LocalDateTime.now());
        tx.setStatus(TransactionStatus.COMPLETED);
        return transactionRepository.save(tx);
    }

    /**
     * Historial de transacciones para una cuenta.
     */
    @Override
    public List<Transaction> getTransactionHistoryForAccount(Long accountId) {
        return transactionRepository.findByAccountId(accountId);
    }

    /**
     * Obtiene transacción por id.
     */
    @Override
    public Transaction getTransactionById(Long id) {
        return transactionRepository.findById(id)
                .orElseThrow(() -> new IllegalStateException("Transacción no encontrada: " + id));
    }
}