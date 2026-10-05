import { compact, hasErrors, isEmail, validateEmail } from './validation'

describe('isEmail', () => {
  it('aceita endereços válidos', () => {
    expect(isEmail('ana@example.com')).toBe(true)
    expect(isEmail('  ana@example.com  ')).toBe(true)
  })

  it('recusa endereços inválidos', () => {
    expect(isEmail('ana')).toBe(false)
    expect(isEmail('ana@')).toBe(false)
    expect(isEmail('ana@example')).toBe(false)
    expect(isEmail('a na@example.com')).toBe(false)
  })
})

describe('validateEmail', () => {
  it('pede o e-mail quando vazio', () => {
    expect(validateEmail('  ')).toBe('Informe seu e-mail.')
  })

  it('explica o formato quando inválido', () => {
    expect(validateEmail('ana')).toContain('e-mail válido')
  })

  it('não devolve erro para e-mail válido', () => {
    expect(validateEmail('ana@example.com')).toBeUndefined()
  })
})

describe('compact e hasErrors', () => {
  it('mantém só os campos com erro', () => {
    expect(compact({ a: 'erro', b: undefined, c: '' })).toEqual({ a: 'erro' })
  })

  it('detecta se há erros', () => {
    expect(hasErrors({})).toBe(false)
    expect(hasErrors({ a: 'erro' })).toBe(true)
  })
})
